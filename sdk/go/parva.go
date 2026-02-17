// Parva Go SDK Client
// ====================
// Official Go client for the Parva Calendar API.
//
// Usage:
//   import "github.com/parva-dev/parva-go"
//   client := parva.NewClient("https://parva.dev")
//   result, _ := client.ConvertDate(2025, 1, 15)

package parva

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Client is the Parva API client.
type Client struct {
	BaseURL    string
	HTTPClient *http.Client
}

// NewClient creates a new Parva client.
func NewClient(baseURL string) *Client {
	return &Client{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// ConvertDate converts a Gregorian date to BS, NS, and tithi.
func (c *Client) ConvertDate(year, month, day int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/convert?year=%d&month=%d&day=%d", c.BaseURL, year, month, day)
	return c.get(url)
}

// GetToday returns today's calendar information.
func (c *Client) GetToday() (map[string]interface{}, error) {
	return c.get(c.BaseURL + "/api/calendar/today")
}

// GetPanchanga returns the full 5-element panchanga for a date.
func (c *Client) GetPanchanga(year, month, day int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/panchanga?year=%d&month=%d&day=%d", c.BaseURL, year, month, day)
	return c.get(url)
}

// CalculateFestival calculates dates for a festival.
func (c *Client) CalculateFestival(festivalID string, year int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/festivals/calculate/%s?year=%d", c.BaseURL, festivalID, year)
	return c.get(url)
}

// UpcomingFestivals returns festivals in the next N days.
func (c *Client) UpcomingFestivals(days int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/festivals/upcoming?days=%d", c.BaseURL, days)
	return c.get(url)
}

// CrossConvert converts a Gregorian date to another calendar system.
func (c *Client) CrossConvert(year, month, day int, targetCalendar string) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/cross/convert?year=%d&month=%d&day=%d&target=%s",
		c.BaseURL, year, month, day, targetCalendar)
	return c.get(url)
}

// CrossConvertAll converts a date to all registered calendar systems.
func (c *Client) CrossConvertAll(year, month, day int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/cross/convert-all?year=%d&month=%d&day=%d", c.BaseURL, year, month, day)
	return c.get(url)
}

// ListCalendars lists all registered calendar plugins.
func (c *Client) ListCalendars() (map[string]interface{}, error) {
	return c.get(c.BaseURL + "/api/calendar/cross/calendars")
}

// ExplainDate returns a step-by-step computation trace.
func (c *Client) ExplainDate(year, month, day int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/explain/date?year=%d&month=%d&day=%d", c.BaseURL, year, month, day)
	return c.get(url)
}

// GetICalFeed returns the iCalendar feed URL.
func (c *Client) GetICalFeed(year int) string {
	return fmt.Sprintf("%s/api/calendar/ical?year=%d", c.BaseURL, year)
}

// EngineHealth returns engine status.
func (c *Client) EngineHealth() (map[string]interface{}, error) {
	return c.get(c.BaseURL + "/api/engine/health")
}

// Forecast returns far-range estimated dates with confidence decay.
func (c *Client) Forecast(festivalID string, years int) (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/calendar/forecast/%s?years=%d", c.BaseURL, festivalID, years)
	return c.get(url)
}

func (c *Client) get(url string) (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body failed: %w", err)
	}

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("JSON decode failed: %w", err)
	}

	return result, nil
}
