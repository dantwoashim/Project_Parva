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
import {
  ArrowUpRight,
  Bookmark,
  CalendarHeart,
  CalendarSync,
  Check,
  Gauge,
  MapPin,
  Trash2,
} from 'lucide-react';

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
          title="API access that grows with your product."
          body="Explore the public API for free, then choose a paid key when your application needs predictable volume, support, and visible usage limits."
          action={<a className="primary-button" href="#checkout">Get API key</a>}
        />

        <section className="pricing-grid" aria-label="API pricing plans">
          {pricingPlans.map((plan, index) => (
            <article key={plan.slug} className={`pricing-card ${plan.slug === selectedTier ? 'is-selected' : ''}`}>
              <div className="pricing-card__top">
                <span className="pricing-card__index">{String(index + 1).padStart(2, '0')}</span>
                <span className="pricing-card__support">{plan.support}</span>
              </div>
              <div className="pricing-card__body">
                <h2>{plan.name}</h2>
                <strong className="pricing-card__price">{plan.price}</strong>
                <p>{plan.body}</p>
              </div>
              <ul className="pricing-card__facts">
                <li><Check aria-hidden="true" /><span>{plan.limit}</span></li>
                <li><Check aria-hidden="true" /><span>{plan.slug === 'free' ? 'IP-based access' : 'Private API key'}</span></li>
              </ul>
              {plan.slug === 'free' ? (
                <a className="ghost-button pricing-card__action" href={apiHref('/calendar/today')}>Try free API <ArrowUpRight aria-hidden="true" /></a>
              ) : (
                <button
                  type="button"
                  className={`pricing-card__action ${plan.slug === selectedTier ? 'primary-button' : 'ghost-button'}`}
                  onClick={() => setSelectedTier(plan.slug)}
                >
                  {plan.slug === selectedTier ? `${plan.name} selected` : `Select ${plan.name}`}
                </button>
              )}
            </article>
          ))}
        </section>

        <header className="commerce-section-heading" id="checkout">
          <div>
            <p className="eyebrow">Activation</p>
            <h2>Request a paid API key</h2>
          </div>
          <p>Choose a plan and payment route. The request stays pending until the payment reference is checked.</p>
        </header>

        <section className="commerce-workspace">
          <form className="checkout-panel" onSubmit={startCheckout}>
            <div className="panel-heading tight">
              <div>
                <p className="eyebrow">Request details</p>
                <strong>{selectedPlan.name} via {providerLabel(provider)}</strong>
              </div>
              <span className="commerce-step">01</span>
            </div>
            <div className="checkout-fields">
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
            </div>
            {selectedQr ? <div className="payment-method-note"><Check aria-hidden="true" /><span>{selectedQr.note}</span></div> : null}
            <button className="primary-button" type="submit">Request access</button>
          </form>

          <aside className="checkout-status-panel">
            <div className="panel-heading tight">
              <div>
                <p className="eyebrow">Payment and activation</p>
                <strong>Confirmation workspace</strong>
              </div>
              <span className="commerce-step">02</span>
            </div>
            {status.text ? <p className={`commerce-status ${status.tone}`}>{status.text}</p> : <p>Request access first. You will receive a payable invoice/reference, then Parva activates your subscription after manual confirmation.</p>}
            {!checkout && selectedQr ? (
              <div className="payment-qr-preview">
                <img src={selectedQr.image} alt={`${selectedQr.label} payment QR`} loading="lazy" />
                <div>
                  <strong>{selectedQr.label}</strong>
                  <p>The invoice number appears after the request is created. Include it with the transfer.</p>
                </div>
              </div>
            ) : null}
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
              <div>
                <p className="eyebrow">Usage</p>
                <strong>Check a key quota</strong>
              </div>
              <Gauge aria-hidden="true" />
            </div>
            <label>
              API key
              <input value={usageKey} onChange={(event) => setUsageKey(event.target.value)} placeholder="parva_live_..." />
            </label>
            <button className="ghost-button" type="submit">Check usage</button>
          </form>
          <div className="usage-summary">
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
      <main className="page-shell profile-page">
        <PageHero
          title="Profile & Saved"
          body="Your current place, followed festivals, and calendar connections stay together on this device."
          action={<Link className="primary-button" to="/festivals">Find festivals</Link>}
        />

        <section className="profile-summary-strip" aria-label="Saved workspace summary">
          <div><MapPin aria-hidden="true" /><span>Place</span><strong>{state.location?.label || 'Kathmandu, Nepal'}</strong></div>
          <div><Bookmark aria-hidden="true" /><span>Saved</span><strong>{savedIds.length} festivals</strong></div>
          <div><CalendarSync aria-hidden="true" /><span>Calendar</span><strong>Ready to connect</strong></div>
        </section>

        <section className="profile-dashboard">
          <article className="profile-place-card">
            <div className="profile-card-icon"><MapPin aria-hidden="true" /></div>
            <div>
              <p className="eyebrow">Current place</p>
              <h2>{state.location?.label || 'Kathmandu, Nepal'}</h2>
              <p>{formatCoordinates(state.location)} / {state.timezone}</p>
            </div>
            <Link className="ghost-button" to="/my-place">Change place <ArrowUpRight aria-hidden="true" /></Link>
          </article>
          <article className="profile-calendar-card">
            <div className="profile-card-icon"><CalendarSync aria-hidden="true" /></div>
            <div>
              <p className="eyebrow">Calendar feeds</p>
              <h2>Keep observances in your calendar</h2>
              <p>Subscribe once, then let your calendar app refresh the feed.</p>
            </div>
            <Link className="ghost-button" to="/integrations">Open integrations <ArrowUpRight aria-hidden="true" /></Link>
          </article>
        </section>

        <section className="saved-festival-panel">
          <header>
            <div>
              <p className="eyebrow">Your calendar</p>
              <h2>Saved festivals</h2>
            </div>
            <strong>{savedIds.length}</strong>
          </header>
          {savedIds.length ? (
            <div className="saved-festival-list" aria-label="Saved festival list">
              {savedIds.map((festivalId, index) => (
                <div key={festivalId} className={`saved-festival-row tone-${(index % 4) + 1}`}>
                  <span className="saved-festival-row__index">{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <Link to={`/festivals/${festivalId}`}>{readableCategory(festivalId)}</Link>
                    <small>Saved on this device</small>
                  </div>
                  <a className="ghost-button" href={buildCalendarFeedUrl(festivalId)}>Calendar</a>
                  <button type="button" className="icon-button" aria-label={`Remove ${readableCategory(festivalId)}`} onClick={() => clearSavedFestival(festivalId)}><Trash2 aria-hidden="true" /></button>
                </div>
              ))}
            </div>
          ) : (
            <div className="saved-empty-state">
              <CalendarHeart aria-hidden="true" />
              <div>
                <h3>Your saved calendar starts here.</h3>
                <p>Follow an observance from the festival list and it will appear here with a direct calendar feed.</p>
              </div>
              <Link className="primary-button" to="/festivals">Browse festivals</Link>
            </div>
          )}
        </section>
      </main>
    </AppChrome>
  );
}
