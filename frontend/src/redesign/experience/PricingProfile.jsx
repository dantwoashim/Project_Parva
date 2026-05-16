import {
  useMemo,
  useState,
  Link,
  billingAPI,
  useTemporalContext,
  useBackendCapabilities,
  apiHref,
  describeSupportError,
  manualPaymentMethods,
  pricingPlans,
  formatCoordinates,
  formatDateTime,
  readableCategory,
  AppChrome,
  PageHero,
} from './ExperienceCommon.jsx';
import {
  buildCalendarFeedUrl,
  readSavedFestivalIds,
  writeSavedFestivalIds,
} from './festival/FestivalUtils.jsx';

function providerLabel(value) {
  if (manualPaymentMethods[value]) return manualPaymentMethods[value].label;
  if (value === 'manual_contact') return 'Personal contact';
  if (value === 'manual_qr') return 'Manual QR payment';
  if (value === 'payoneer') return 'Payoneer invoice';
  if (value === 'esewa') return 'eSewa';
  return 'Khalti';
}

function formatMinorCurrency(amountMinor, currency = 'NPR') {
  const amount = Number(amountMinor);
  if (!Number.isFinite(amount)) return currency || 'NPR';
  return `${currency || 'NPR'} ${(amount / 100).toLocaleString('en', { maximumFractionDigits: 0 })}`;
}

export function RedesignApiPricing() {
  const capabilities = useBackendCapabilities();
  const billingAvailable = capabilities.isEnabled('billingEnterprise');
  const [selectedTier, setSelectedTier] = useState('starter');
  const [provider, setProvider] = useState('manual_bank_qr');
  const [customer, setCustomer] = useState({ email: '', name: '', country: 'NP' });
  const [checkout, setCheckout] = useState(null);
  const [apiKeyResult, setApiKeyResult] = useState(null);
  const [usageKey, setUsageKey] = useState('');
  const [usage, setUsage] = useState(null);
  const [status, setStatus] = useState({ tone: 'idle', text: '' });

  const paidPlans = useMemo(() => pricingPlans.filter((plan) => plan.slug !== 'free'), []);
  const selectedPlan = pricingPlans.find((plan) => plan.slug === selectedTier) || pricingPlans[1];
  const selectedQr = manualPaymentMethods[provider] || null;

  const updateCustomer = (field, value) => {
    setCustomer((current) => ({ ...current, [field]: value }));
  };

  const startCheckout = async (event) => {
    event.preventDefault();
    if (!billingAvailable) {
      setStatus({ tone: 'error', text: 'Billing API is controlled under the enterprise preview route profile.' });
      return;
    }
    setStatus({ tone: 'loading', text: 'Creating payment request...' });
    setApiKeyResult(null);
    try {
      const payload = {
        ...customer,
        tier: selectedTier,
        provider,
      };
      const result = await billingAPI.createCheckout(payload);
      setCheckout(result);
      setStatus({
        tone: 'success',
        text: 'Payment request created. Scan the selected QR, include the invoice number as remarks if possible, then send your screenshot or reference for activation.',
      });
    } catch (error) {
      setStatus({ tone: 'error', text: describeSupportError(error, 'Checkout could not be created.') });
    }
  };

  const createApiKey = async () => {
    if (!checkout?.checkout_id) return;
    if (!billingAvailable) {
      setStatus({ tone: 'error', text: 'API key activation is controlled under the enterprise preview route profile.' });
      return;
    }
    setStatus({ tone: 'loading', text: 'Checking activation status...' });
    try {
      const result = await billingAPI.createKey({ checkout_id: checkout.checkout_id, name: `${selectedPlan.name} production key` });
      setApiKeyResult(result);
      if (result.api_key) setUsageKey(result.api_key);
      setStatus({ tone: 'success', text: result.message || 'API key created.' });
    } catch (error) {
      setStatus({ tone: 'error', text: describeSupportError(error, 'API key could not be created.') });
    }
  };

  const loadUsage = async (event) => {
    event.preventDefault();
    if (!billingAvailable) {
      setStatus({ tone: 'error', text: 'Usage lookup is controlled under the enterprise preview route profile.' });
      return;
    }
    setStatus({ tone: 'loading', text: 'Loading usage...' });
    try {
      const result = await billingAPI.getUsage(usageKey.trim());
      setUsage(result);
      setStatus({ tone: 'success', text: 'Usage loaded.' });
    } catch (error) {
      setStatus({ tone: 'error', text: describeSupportError(error, 'Usage could not be loaded.') });
    }
  };

  return (
    <AppChrome>
      <main className="page-shell api-commerce-page">
        <PageHero
          title="Start with a free API. Upgrade by manual payment when you need volume."
          body="Parva supports free IP quotas, paid API keys, QR/contact payment requests, Payoneer invoices, usage limits, and admin-confirmed activation while merchant checkout accounts are pending."
          action={<a className="primary-button" href="#checkout">Get API key</a>}
        />

        <section className="pricing-grid" aria-label="API pricing plans">
          {pricingPlans.map((plan) => (
            <article key={plan.slug} className={`pricing-card ${plan.slug === selectedTier ? 'is-selected' : ''}`}>
              <div>
                <span>{plan.support}</span>
                <h2>{plan.name}</h2>
                <strong>{plan.price}</strong>
                <p>{plan.body}</p>
              </div>
              <dl>
                <div><dt>Limit</dt><dd>{plan.limit}</dd></div>
                <div><dt>Auth</dt><dd>{plan.slug === 'free' ? 'IP-based' : 'API key'}</dd></div>
              </dl>
              {plan.slug === 'free' ? (
                <a className="ghost-button" href={apiHref('/calendar/today')}>Try free API</a>
              ) : (
                <button type="button" onClick={() => setSelectedTier(plan.slug)}>Select {plan.name}</button>
              )}
            </article>
          ))}
        </section>

        <section className="commerce-workspace" id="checkout">
          <form className="checkout-panel" onSubmit={startCheckout}>
            <div className="panel-heading tight">
              <p className="eyebrow">Checkout</p>
              <strong>{selectedPlan.name} via {providerLabel(provider)}</strong>
            </div>
            <label>
              Email
              <input value={customer.email} onChange={(event) => updateCustomer('email', event.target.value)} type="email" required placeholder="you@company.com" />
            </label>
            <label>
              Name
              <input value={customer.name} onChange={(event) => updateCustomer('name', event.target.value)} placeholder="Billing contact" />
            </label>
            <label>
              Tier
              <select value={selectedTier} onChange={(event) => setSelectedTier(event.target.value)}>
                {paidPlans.map((plan) => <option key={plan.slug} value={plan.slug}>{plan.name} - {plan.price}</option>)}
              </select>
            </label>
            <label>
              Payment
              <select value={provider} onChange={(event) => setProvider(event.target.value)}>
                <option value="manual_bank_qr">Bank QR</option>
                <option value="manual_esewa_qr">eSewa QR</option>
                <option value="manual_khalti_qr">Khalti QR</option>
                <option value="manual_contact">Personal contact</option>
                <option value="payoneer">Payoneer invoice</option>
              </select>
            </label>
            {selectedQr ? (
              <div className="payment-qr-preview compact">
                <img src={selectedQr.image} alt={`${selectedQr.label} payment QR`} loading="lazy" />
                <div>
                  <strong>{selectedQr.label}</strong>
                  <p>{selectedQr.note}</p>
                </div>
              </div>
            ) : null}
            <button className="primary-button" type="submit">Request access</button>
          </form>

          <aside className="checkout-status-panel">
            <div className="panel-heading tight">
              <p className="eyebrow">Activation</p>
              <strong>Manual confirmation only</strong>
            </div>
            {status.text ? <p className={`commerce-status ${status.tone}`}>{status.text}</p> : <p>Request access first. You will receive a payable invoice/reference, then Parva activates your subscription after manual confirmation.</p>}
            {checkout ? (
              <div className="checkout-receipt">
                <span>{checkout.invoice_number || checkout.invoice_id}</span>
                <strong>{checkout.tier} · {formatMinorCurrency(checkout.amount_minor, checkout.currency)}</strong>
                <p>{checkout.message || 'Invoice stored. Send your payment reference to Parva support for activation.'}</p>
                {selectedQr ? (
                  <div className="payment-qr-preview">
                    <img src={selectedQr.image} alt={`${selectedQr.label} payment QR`} loading="lazy" />
                    <div>
                      <strong>Scan {selectedQr.shortLabel}</strong>
                      <p>Remarks/reference: {checkout.invoice_number || checkout.invoice_id}. After payment, send the screenshot or transaction reference so the API key can be activated.</p>
                    </div>
                  </div>
                ) : null}
                <button type="button" onClick={createApiKey}>Check activation and reveal API key</button>
              </div>
            ) : null}
            {apiKeyResult ? (
              <div className="api-key-reveal">
                <span>One-time key</span>
                <code>{apiKeyResult.api_key || 'Existing key hidden'}</code>
                <p>{apiKeyResult.message}</p>
              </div>
            ) : null}
          </aside>
        </section>

        <section className="usage-console">
          <form onSubmit={loadUsage}>
            <div className="panel-heading tight">
              <p className="eyebrow">Usage</p>
              <strong>Quota visibility</strong>
            </div>
            <label>
              API key
              <input value={usageKey} onChange={(event) => setUsageKey(event.target.value)} placeholder="parva_live_..." />
            </label>
            <button type="submit">Check usage</button>
          </form>
          <div className="usage-meter">
            {usage ? (
              <>
                <span>{usage.tier} · {usage.period}</span>
                <strong>{usage.used} / {usage.limit}</strong>
                <p>{usage.remaining} requests remaining until {formatDateTime(usage.reset_at)}</p>
              </>
            ) : (
              <p>Use a paid key to inspect monthly usage, or leave it blank to see the current free IP bucket.</p>
            )}
          </div>
        </section>
      </main>
    </AppChrome>
  );
}

export function RedesignProfileSaved() {
  const { state } = useTemporalContext();
  const [savedIds, setSavedIds] = useState(() => readSavedFestivalIds());

  const clearSavedFestival = (festivalId) => {
    setSavedIds((current) => {
      const next = current.filter((item) => item !== festivalId);
      writeSavedFestivalIds(next);
      return next;
    });
  };

  return (
    <AppChrome>
      <main className="page-shell simple-grid">
        <PageHero title="Profile & Saved" body="A private workspace for place context, saved observances, and calendar connections." />
        <article className="panel"><h2>Current place</h2><p>{formatCoordinates(state.location)} · {state.timezone}</p><Link className="text-link" to="/my-place">Load place data</Link></article>
        <article className="panel saved-festival-panel">
          <h2>Saved festivals</h2>
          {savedIds.length ? (
            <div className="saved-festival-list" aria-label="Saved festival list">
              {savedIds.map((festivalId) => (
                <div key={festivalId}>
                  <Link className="text-link" to={`/festivals/${festivalId}`}>{readableCategory(festivalId)}</Link>
                  <a href={buildCalendarFeedUrl(festivalId)}>Calendar</a>
                  <button type="button" onClick={() => clearSavedFestival(festivalId)}>Remove</button>
                </div>
              ))}
            </div>
          ) : (
            <p>Save observances from the festival calendar to build a personal ritual year.</p>
          )}
          <Link className="text-link" to="/festivals">Browse festivals</Link>
        </article>
        <article className="panel"><h2>Calendar export</h2><p>Subscribe to Parva calendars from the integrations page.</p><Link className="text-link" to="/integrations">Open integrations</Link></article>
      </main>
    </AppChrome>
  );
}
