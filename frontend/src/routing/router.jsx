/* eslint-disable react-refresh/only-export-components */
import {
  Children,
  createContext,
  forwardRef,
  isValidElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

const RouterContext = createContext(null);
const ParamsContext = createContext({});

function locationFromUrl(value, state = null) {
  const url = new URL(value, 'http://parva.local');
  return {
    pathname: url.pathname || '/',
    search: url.search,
    hash: url.hash,
    state,
    key: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
  };
}

function currentBrowserLocation() {
  return locationFromUrl(window.location.href, window.history.state);
}

function toHref(to) {
  if (typeof to === 'string') {
    return to;
  }
  return `${to?.pathname || ''}${to?.search || ''}${to?.hash || ''}` || '/';
}

function RouterProvider({ children, location, navigate }) {
  const value = useMemo(() => ({ location, navigate }), [location, navigate]);
  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}

export function BrowserRouter({ children }) {
  const [location, setLocation] = useState(currentBrowserLocation);

  useEffect(() => {
    const onPopState = () => setLocation(currentBrowserLocation());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = useCallback((to, options = {}) => {
    const href = toHref(to);
    const destination = new URL(href, window.location.href);
    if (destination.origin !== window.location.origin) {
      window.location.assign(destination.href);
      return;
    }

    const method = options.replace ? 'replaceState' : 'pushState';
    window.history[method](options.state ?? null, '', destination.href);
    setLocation(currentBrowserLocation());
  }, []);

  return (
    <RouterProvider location={location} navigate={navigate}>
      {children}
    </RouterProvider>
  );
}

export function MemoryRouter({ children, initialEntries = ['/'], initialIndex }) {
  const entries = useMemo(
    () => (initialEntries.length ? initialEntries : ['/']).map((entry) => toHref(entry)),
    [initialEntries],
  );
  const startingIndex = Math.min(
    Math.max(initialIndex ?? entries.length - 1, 0),
    entries.length - 1,
  );
  const [location, setLocation] = useState(() => locationFromUrl(entries[startingIndex]));

  const navigate = useCallback((to, options = {}) => {
    setLocation(locationFromUrl(toHref(to), options.state ?? null));
  }, []);

  return (
    <RouterProvider location={location} navigate={navigate}>
      {children}
    </RouterProvider>
  );
}

function useRouter() {
  const router = useContext(RouterContext);
  if (!router) {
    throw new Error('Routing components must be rendered inside BrowserRouter or MemoryRouter.');
  }
  return router;
}

export function useLocation() {
  return useRouter().location;
}

export function useNavigate() {
  return useRouter().navigate;
}

export function useParams() {
  return useContext(ParamsContext);
}

function pathMatch(pattern, pathname) {
  if (pattern === '*') {
    return {};
  }

  const patternParts = pattern.split('/').filter(Boolean);
  const pathParts = pathname.split('/').filter(Boolean);
  const wildcardIndex = patternParts.indexOf('*');
  if (wildcardIndex === -1 && patternParts.length !== pathParts.length) {
    return null;
  }
  if (wildcardIndex !== -1 && pathParts.length < wildcardIndex) {
    return null;
  }

  const params = {};
  for (let index = 0; index < patternParts.length; index += 1) {
    const expected = patternParts[index];
    if (expected === '*') {
      params['*'] = pathParts.slice(index).map(decodeURIComponent).join('/');
      return params;
    }

    const actual = pathParts[index];
    if (actual === undefined) {
      return null;
    }
    if (expected.startsWith(':')) {
      params[expected.slice(1)] = decodeURIComponent(actual);
    } else if (expected.toLowerCase() !== actual.toLowerCase()) {
      return null;
    }
  }
  return params;
}

export function Routes({ children }) {
  const { pathname } = useLocation();
  for (const child of Children.toArray(children)) {
    if (!isValidElement(child)) {
      continue;
    }
    const params = pathMatch(child.props.path, pathname);
    if (params !== null) {
      return (
        <ParamsContext.Provider value={params}>
          {child.props.element}
        </ParamsContext.Provider>
      );
    }
  }
  return null;
}

export function Route({ element = null }) {
  return element;
}

export function Navigate({ to, replace = false, state = null }) {
  const navigate = useNavigate();
  useEffect(() => {
    navigate(to, { replace, state });
  }, [navigate, replace, state, to]);
  return null;
}

function shouldHandleLink(event, target, download) {
  return (
    !event.defaultPrevented
    && event.button === 0
    && !event.metaKey
    && !event.ctrlKey
    && !event.shiftKey
    && !event.altKey
    && (!target || target === '_self')
    && !download
  );
}

export const Link = forwardRef(function Link(
  {
    children,
    download,
    onClick,
    reloadDocument = false,
    replace = false,
    state = null,
    target,
    to,
    ...props
  },
  ref,
) {
  const navigate = useNavigate();
  const href = toHref(to);

  const handleClick = (event) => {
    onClick?.(event);
    if (!reloadDocument && shouldHandleLink(event, target, download)) {
      const destination = new URL(href, window.location.href);
      if (destination.origin === window.location.origin) {
        event.preventDefault();
        navigate(href, { replace, state });
      }
    }
  };

  return (
    <a
      {...props}
      ref={ref}
      href={href}
      data-discover="true"
      target={target}
      download={download}
      onClick={handleClick}
    >
      {children}
    </a>
  );
});

export const NavLink = forwardRef(function NavLink(
  { 'aria-current': ariaCurrent = 'page', children, className, end = false, style, to, ...props },
  ref,
) {
  const location = useLocation();
  const href = toHref(to);
  const destination = new URL(href, window.location.href);
  const targetPath = destination.pathname.replace(/\/+$/, '') || '/';
  const currentPath = location.pathname.replace(/\/+$/, '') || '/';
  const isActive = end
    ? currentPath === targetPath
    : currentPath === targetPath || currentPath.startsWith(`${targetPath}/`);
  const state = { isActive, isPending: false, isTransitioning: false };

  return (
    <Link
      {...props}
      ref={ref}
      to={to}
      aria-current={isActive ? ariaCurrent : undefined}
      className={typeof className === 'function' ? className(state) : className}
      style={typeof style === 'function' ? style(state) : style}
    >
      {typeof children === 'function' ? children(state) : children}
    </Link>
  );
});
