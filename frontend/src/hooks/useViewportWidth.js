import { useEffect, useState } from 'react';

const DEFAULT_VIEWPORT_WIDTH = 1440;

function readViewportWidth() {
  if (typeof window === 'undefined') {
    return DEFAULT_VIEWPORT_WIDTH;
  }

  return window.innerWidth || document.documentElement?.clientWidth || DEFAULT_VIEWPORT_WIDTH;
}

export function useViewportWidth() {
  const [viewportWidth, setViewportWidth] = useState(() => readViewportWidth());

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    function handleResize() {
      setViewportWidth(readViewportWidth());
    }

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return viewportWidth;
}
