import { createContext, useContext } from 'react';

export const ParvaToastContext = createContext(null);

export function useParvaToast() {
  const value = useContext(ParvaToastContext);
  if (!value) {
    return {
      notify: () => undefined,
      dismissToast: () => undefined,
    };
  }
  return value;
}
