import { useCallback, useMemo, useRef, useState } from 'react';
import {
  AnimatePresence,
  domAnimation,
  LazyMotion,
  m,
  MotionConfig,
  useReducedMotion,
} from 'motion/react';
import { AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';
import { ParvaToastContext } from './ParvaToastContext';
import './ParvaMotion.css';

const toastIcons = {
  success: CheckCircle2,
  warning: AlertTriangle,
  info: Info,
};

const motionElements = {
  article: m.article,
  div: m.div,
  li: m.li,
  section: m.section,
};

export function ParvaMotionProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const counter = useRef(0);

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const notify = useCallback((message, options = {}) => {
    const id = ++counter.current;
    const toast = {
      id,
      message,
      detail: options.detail || '',
      tone: options.tone || 'success',
    };
    setToasts((current) => [...current.slice(-2), toast]);
    window.setTimeout(() => dismissToast(id), options.duration || 2600);
    return id;
  }, [dismissToast]);

  const value = useMemo(() => ({ notify, dismissToast }), [dismissToast, notify]);

  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig
        reducedMotion="user"
        transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      >
        <ParvaToastContext.Provider value={value}>
          {children}
          <ToastViewport toasts={toasts} onDismiss={dismissToast} />
        </ParvaToastContext.Provider>
      </MotionConfig>
    </LazyMotion>
  );
}

export function RouteTransition({ routeKey, children }) {
  const reduceMotion = useReducedMotion();

  return (
    <m.div
      key={routeKey}
      className="route-presence"
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </m.div>
  );
}

export function Reveal({
  children,
  className = '',
  delay = 0,
  distance = 10,
  as = 'div',
}) {
  const reduceMotion = useReducedMotion();
  const Component = motionElements[as] || m.div;
  return (
    <Component
      className={className}
      initial={reduceMotion ? false : { opacity: 0, y: distance }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: reduceMotion ? 0 : 0.34, delay: reduceMotion ? 0 : delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </Component>
  );
}

function ToastViewport({ toasts, onDismiss }) {
  const reduceMotion = useReducedMotion();
  return (
    <div className="parva-toast-viewport" role="status" aria-live="polite" aria-atomic="true">
      <AnimatePresence initial={false}>
        {toasts.map((toast) => {
          const Icon = toastIcons[toast.tone] || Info;
          return (
            <m.article
              key={toast.id}
              className={`parva-toast is-${toast.tone}`}
              initial={reduceMotion ? false : { opacity: 0, y: 14, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={reduceMotion ? { opacity: 0 } : { opacity: 0, x: 18, scale: 0.97 }}
              transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, 0.36, 1] }}
            >
              <Icon aria-hidden="true" />
              <div>
                <strong>{toast.message}</strong>
                {toast.detail ? <span>{toast.detail}</span> : null}
              </div>
              <button type="button" onClick={() => onDismiss(toast.id)} aria-label="Dismiss notification">
                <X aria-hidden="true" />
              </button>
            </m.article>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
