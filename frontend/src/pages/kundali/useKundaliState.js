import { useMemo, useState } from 'react';
import { useMemberContext } from '../../context/useMemberContext';
import { kundaliAPI, placesAPI } from '../../services/api';
import { describeSupportError } from '../../services/errorFormatting';
import {
  buildChartFocus,
  buildInsightHighlights,
  buildSignature,
  buildThesis,
} from './kundaliPresentation';
import { buildSavedReading, resolveBirthInput } from './kundaliFormState';

const EMPTY_FORM = {
  birthDay: '',
  birthMonth: '',
  birthYear: '',
  birthTime: '',
  placeQuery: '',
  latitude: '',
  longitude: '',
  timezone: '',
};

export function useKundaliState() {
  const { saveReading } = useMemberContext();
  const [form, setForm] = useState(EMPTY_FORM);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [searchAttribution, setSearchAttribution] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [graphMeta, setGraphMeta] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeTab, setActiveTab] = useState('chart');
  const [submittedInput, setSubmittedInput] = useState(null);

  const resolvedInput = useMemo(() => resolveBirthInput(form), [form]);
  const signature = useMemo(() => buildSignature(payload), [payload]);
  const thesis = useMemo(() => buildThesis(payload, graphPayload), [graphPayload, payload]);
  const insightHighlights = useMemo(() => buildInsightHighlights(payload, graphPayload), [graphPayload, payload]);
  const focusPayload = useMemo(
    () => ({
      ...payload,
      houses: graphPayload?.layout?.house_nodes || payload?.houses || [],
      grahas: payload?.grahas || {},
    }),
    [graphPayload, payload],
  );
  const focus = useMemo(() => buildChartFocus(selectedNode, focusPayload), [focusPayload, selectedNode]);

  async function handlePlaceSearch(event) {
    event.preventDefault();
    setSearchLoading(true);
    setSearchError('');

    try {
      const response = await placesAPI.search({ query: form.placeQuery, limit: 5 });
      setSearchResults(response.items || []);
      setSearchAttribution(response.attribution || '');
      if (!(response.items || []).length) {
        setSearchError('No matching places were found. Try a city, district, or country.');
      }
    } catch (error) {
      setSearchResults([]);
      setSearchAttribution('');
      setSearchError(describeSupportError(error, 'Place search is unavailable right now.'));
    } finally {
      setSearchLoading(false);
    }
  }

  function applyPlace(item) {
    setForm((current) => ({
      ...current,
      placeQuery: item.label,
      latitude: String(item.latitude),
      longitude: String(item.longitude),
      timezone: item.timezone,
    }));
    setSearchResults([]);
    setSearchError('');
  }

  async function handleGenerate(event) {
    event.preventDefault();

    if (resolvedInput.errors.length || !resolvedInput.value) {
      setSubmitError(resolvedInput.errors[0] || 'Enter complete birth details before generating the chart.');
      return;
    }

    setLoading(true);
    setSubmitError('');

    try {
      const nextInput = resolvedInput.value;
      const [kundali, graphEnvelope] = await Promise.all([
        kundaliAPI.getKundali({
          datetime: nextInput.datetime,
          lat: nextInput.latitude,
          lon: nextInput.longitude,
          tz: nextInput.timezone,
        }),
        kundaliAPI.getGraphEnvelope({
          datetime: nextInput.datetime,
          lat: nextInput.latitude,
          lon: nextInput.longitude,
          tz: nextInput.timezone,
        }),
      ]);

      setPayload(kundali);
      setGraphPayload(graphEnvelope.data || null);
      setGraphMeta(graphEnvelope.meta || null);
      setSelectedNode(null);
      setActiveTab('chart');
      setSubmittedInput(nextInput);
    } catch (error) {
      setPayload(null);
      setGraphPayload(null);
      setGraphMeta(null);
      setSubmittedInput(null);
      setSubmitError(describeSupportError(error, 'Birth chart generation failed.'));
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveReading() {
    if (!submittedInput || !payload) return;
    await saveReading(buildSavedReading(submittedInput, payload));
  }

  return {
    form,
    setForm,
    advancedOpen,
    setAdvancedOpen,
    searchResults,
    searchLoading,
    searchError,
    searchAttribution,
    submitError,
    loading,
    payload,
    graphPayload,
    graphMeta,
    selectedNode,
    setSelectedNode,
    activeTab,
    setActiveTab,
    submittedInput,
    signature,
    thesis,
    insightHighlights,
    focus,
    handlePlaceSearch,
    applyPlace,
    handleGenerate,
    handleSaveReading,
  };
}
