import {
  ArrowRight,
  Building2,
  Check,
  Code2,
  FileCheck2,
  Scale,
  ShieldCheck,
} from 'lucide-react';
import { Link } from '@parva/router';
import '../../styles/polish/15-positioning-licensing.css';

const commercialPlans = [
  {
    name: 'Single Product',
    price: 'NPR 100K',
    detail: 'per vendor, per year',
    features: ['One named proprietary product', 'Production embedding rights', 'Private modifications', 'Email onboarding'],
  },
  {
    name: 'Product Suite',
    price: 'NPR 200K',
    detail: 'per vendor, per year',
    features: ['Up to three named products', 'Web, server, and mobile deployment', 'Private modifications', 'Upgrade guidance'],
    featured: true,
  },
  {
    name: 'OEM Portfolio',
    price: 'NPR 300K',
    detail: 'per vendor, per year',
    features: ['Up to five named products', 'Customer-hosted deployment', 'Priority integration review', 'Redistribution terms in the agreement'],
  },
];

const commercialMail = `mailto:twodan033@gmail.com?subject=${encodeURIComponent('Project Parva commercial embedding license')}`;

export function RedesignLicensing() {
  return (
    <main className="licensing-page" data-testid="licensing-page">
      <section className="licensing-hero">
        <div>
          <span className="eyebrow">Dual licensing</span>
          <h1>Build openly or embed privately.</h1>
          <p>Use Project Parva under AGPL-3.0-or-later with no license fee, or sign an annual commercial agreement for proprietary embedding.</p>
        </div>
        <div className="licensing-hero__mark" aria-hidden="true">
          <Scale />
          <span>Two clear paths</span>
        </div>
      </section>

      <section className="license-paths" aria-label="Project Parva licensing paths">
        <article className="license-path license-path--open">
          <header>
            <span className="license-path__icon"><Code2 aria-hidden="true" /></span>
            <div><small>Open-source path</small><h2>AGPL-3.0-or-later</h2></div>
          </header>
          <strong className="license-price">NPR 0 <small>license fee</small></strong>
          <p>Commercial use is allowed. Covered source and modifications stay under the AGPL, and network users receive access to the corresponding source as required by the license.</p>
          <ul>
            <li><Check aria-hidden="true" /> Public and commercial use</li>
            <li><Check aria-hidden="true" /> Modification and self-hosting</li>
            <li><Check aria-hidden="true" /> Source-sharing obligations apply</li>
            <li><Check aria-hidden="true" /> Copyright and license notices stay intact</li>
          </ul>
          <div className="license-actions">
            <a href="https://github.com/dantwoashim/Project_Parva">View source <ArrowRight aria-hidden="true" /></a>
            <a href="https://www.gnu.org/licenses/agpl-3.0.en.html">Read AGPL terms</a>
          </div>
        </article>

        <article className="license-path license-path--commercial">
          <header>
            <span className="license-path__icon"><Building2 aria-hidden="true" /></span>
            <div><small>Proprietary path</small><h2>Commercial embedding</h2></div>
          </header>
          <strong className="license-price">NPR 100-300K <small>per vendor / year</small></strong>
          <p>A signed commercial agreement grants proprietary embedding rights for the named Project Parva components, products, and deployment scope.</p>
          <ul>
            <li><Check aria-hidden="true" /> Closed-source product integration</li>
            <li><Check aria-hidden="true" /> Private application modifications</li>
            <li><Check aria-hidden="true" /> Named deployment and redistribution rights</li>
            <li><Check aria-hidden="true" /> Commercial onboarding options</li>
          </ul>
          <div className="license-actions">
            <a className="license-primary-action" href={commercialMail}>Request terms <ArrowRight aria-hidden="true" /></a>
            <a href="https://github.com/dantwoashim/Project_Parva/blob/main/docs/COMMERCIAL_LICENSING.md">Read the overview</a>
          </div>
        </article>
      </section>

      <section className="commercial-pricing" aria-labelledby="commercial-pricing-title">
        <header>
          <span className="eyebrow">Annual embedding license</span>
          <h2 id="commercial-pricing-title">Choose the product scope.</h2>
          <p>Every plan covers one vendor legal entity. Taxes, custom engineering, uptime commitments, and managed hosting are quoted separately.</p>
        </header>
        <div className="commercial-plan-grid">
          {commercialPlans.map((plan) => (
            <article key={plan.name} className={plan.featured ? 'is-featured' : ''}>
              {plan.featured ? <span className="plan-label">Most practical</span> : null}
              <h3>{plan.name}</h3>
              <strong>{plan.price}</strong>
              <small>{plan.detail}</small>
              <ul>
                {plan.features.map((feature) => <li key={feature}><Check aria-hidden="true" />{feature}</li>)}
              </ul>
              <a href={commercialMail}>Discuss scope <ArrowRight aria-hidden="true" /></a>
            </article>
          ))}
        </div>
      </section>

      <section className="license-clarity" aria-labelledby="license-clarity-title">
        <div>
          <span className="license-path__icon"><FileCheck2 aria-hidden="true" /></span>
          <span className="eyebrow">Clear separation</span>
          <h2 id="license-clarity-title">Embedding and hosted API access are different products.</h2>
        </div>
        <dl>
          <div><dt>Commercial license</dt><dd>Rights to place Project Parva code inside a proprietary product.</dd></div>
          <div><dt>API plan</dt><dd>Usage quota for the hosted Project Parva service.</dd></div>
          <div><dt>Support agreement</dt><dd>Response times, managed updates, deployment help, and custom work.</dd></div>
        </dl>
        <Link to="/pricing">View hosted API pricing <ArrowRight aria-hidden="true" /></Link>
      </section>

      <section className="license-footer-cta">
        <ShieldCheck aria-hidden="true" />
        <div>
          <h2>Put the exact products and deployment rights in writing.</h2>
          <p>This page is a pricing and scope overview. The signed commercial agreement controls the granted rights.</p>
        </div>
        <a href={commercialMail}>Start a license request</a>
      </section>
    </main>
  );
}
