package parva

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

type ConfidenceMeta struct {
	Level string  `json:"level"`
	Score float64 `json:"score"`
}

type ProvenanceMeta struct {
	SnapshotID  *string `json:"snapshot_id"`
	DatasetHash *string `json:"dataset_hash"`
	RulesHash   *string `json:"rules_hash"`
	VerifyURL   *string `json:"verify_url"`
	Signature   *string `json:"signature"`
}

type UncertaintyMeta struct {
	IntervalHours *float64 `json:"interval_hours"`
	BoundaryRisk  string   `json:"boundary_risk"`
}

type PolicyMeta struct {
	Profile      string `json:"profile"`
	Jurisdiction string `json:"jurisdiction"`
	Advisory     bool   `json:"advisory"`
}

type ResponseMeta struct {
	Confidence  ConfidenceMeta  `json:"confidence"`
	Method      string          `json:"method"`
	Provenance  ProvenanceMeta  `json:"provenance"`
	Uncertainty UncertaintyMeta `json:"uncertainty"`
	TraceID     *string         `json:"trace_id"`
	Policy      PolicyMeta      `json:"policy"`
}

type Envelope struct {
	Data json.RawMessage `json:"data"`
	Meta ResponseMeta    `json:"meta"`
}

type Client struct {
	BaseURL    string
	HTTPClient *http.Client
	Retries    int
	Backoff    time.Duration
}

func NewClient(baseURL string) *Client {
	if baseURL == "" {
		baseURL = "http://localhost:8000/v5/api"
	}
	return &Client{
		BaseURL:    strings.TrimRight(baseURL, "/"),
		HTTPClient: &http.Client{Timeout: 20 * time.Second},
		Retries:    2,
		Backoff:    300 * time.Millisecond,
	}
}

func (c *Client) get(path string, params map[string]string) (*Envelope, error) {
	ctx := context.Background()
	return c.getWithContext(ctx, path, params)
}

func (c *Client) getWithContext(ctx context.Context, path string, params map[string]string) (*Envelope, error) {
	u, err := url.Parse(c.BaseURL + path)
	if err != nil {
		return nil, err
	}
	q := u.Query()
	for k, v := range params {
		if v != "" {
			q.Set(k, v)
		}
	}
	u.RawQuery = q.Encode()

	var lastErr error
	for attempt := 0; attempt <= c.Retries; attempt++ {
		req, reqErr := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
		if reqErr != nil {
			return nil, reqErr
		}
		resp, doErr := c.HTTPClient.Do(req)
		if doErr != nil {
			lastErr = doErr
		} else {
			body, readErr := io.ReadAll(resp.Body)
			resp.Body.Close()
			if readErr != nil {
				lastErr = readErr
			} else if resp.StatusCode >= 200 && resp.StatusCode < 300 {
				env, parseErr := parseEnvelope(body)
				if parseErr != nil {
					return nil, parseErr
				}
				return env, nil
			} else {
				lastErr = fmt.Errorf("parva api %d: %s", resp.StatusCode, string(body))
				if resp.StatusCode < 500 || attempt >= c.Retries {
					return nil, lastErr
				}
			}
		}
		if attempt < c.Retries {
			time.Sleep(c.Backoff * time.Duration(1<<attempt))
		}
	}
	if lastErr != nil {
		return nil, lastErr
	}
	return nil, fmt.Errorf("request failed")
}

func parseEnvelope(body []byte) (*Envelope, error) {
	var env Envelope
	if err := json.Unmarshal(body, &env); err == nil && len(env.Data) > 0 {
		return &env, nil
	}

	// v3 compatibility fallback
	compat := Envelope{
		Data: json.RawMessage(body),
		Meta: ResponseMeta{
			Confidence: ConfidenceMeta{Level: "unknown", Score: 0.5},
			Method:     "unknown",
			Uncertainty: UncertaintyMeta{
				BoundaryRisk: "unknown",
			},
			Policy: PolicyMeta{
				Profile:      "np-mainstream",
				Jurisdiction: "NP",
				Advisory:     true,
			},
		},
	}
	return &compat, nil
}

func DecodeData[T any](env *Envelope, out *T) error {
	return json.Unmarshal(env.Data, out)
}

func (c *Client) Today() (*Envelope, error) {
	return c.get("/calendar/today", map[string]string{})
}

func (c *Client) Convert(date string) (*Envelope, error) {
	return c.get("/calendar/convert", map[string]string{"date": date})
}

func (c *Client) Panchanga(date string) (*Envelope, error) {
	params := map[string]string{}
	if date != "" {
		params["date"] = date
	}
	return c.get("/calendar/panchanga", params)
}

func (c *Client) Upcoming(days int) (*Envelope, error) {
	return c.get("/festivals/upcoming", map[string]string{"days": strconv.Itoa(days)})
}

func (c *Client) ExplainFestival(festivalID string, year int) (*Envelope, error) {
	return c.get("/festivals/"+festivalID+"/explain", map[string]string{"year": strconv.Itoa(year)})
}

func (c *Client) ExplainTrace(traceID string) (*Envelope, error) {
	return c.get("/explain/"+traceID, map[string]string{})
}

func (c *Client) Resolve(date string, profile string, latitude float64, longitude float64, includeTrace bool) (*Envelope, error) {
	if profile == "" {
		profile = "np-mainstream"
	}
	return c.get("/resolve", map[string]string{
		"date":          date,
		"profile":       profile,
		"latitude":      fmt.Sprintf("%f", latitude),
		"longitude":     fmt.Sprintf("%f", longitude),
		"include_trace": strconv.FormatBool(includeTrace),
	})
}

func (c *Client) SpecConformance() (*Envelope, error) {
	return c.get("/spec/conformance", map[string]string{})
}

func (c *Client) VerifyTrace(traceID string) (*Envelope, error) {
	return c.get("/provenance/verify/trace/"+traceID, map[string]string{})
}
