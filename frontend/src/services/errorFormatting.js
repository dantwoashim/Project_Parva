function normalizeRequestId(error) {
  if (typeof error?.requestId === 'string' && error.requestId.trim()) {
    return error.requestId.trim();
  }
  if (typeof error?.request_id === 'string' && error.request_id.trim()) {
    return error.request_id.trim();
  }
  return null;
}

export function describeSupportError(error, fallback) {
  if (typeof error === 'string' && error.trim()) {
    return cleanSupportMessage(error.trim(), fallback);
  }

  const message = typeof error?.message === 'string' && error.message.trim()
    ? error.message.trim()
    : fallback;
  const requestId = normalizeRequestId(error);
  const cleanMessage = cleanSupportMessage(message, fallback);
  if (!requestId) {
    return cleanMessage;
  }
  return `${cleanMessage} Support reference: ${requestId}.`;
}

export function pickRejectedReason(...results) {
  return results.find((result) => result?.status === 'rejected')?.reason ?? null;
}

function cleanSupportMessage(message, fallback = 'Something went wrong.') {
  const raw = String(message || '').trim();
  if (!raw) return fallback;

  const looksLikeHtml = /<!doctype|<html|<body|<h1|<\/?[a-z][\s\S]*>/i.test(raw);
  if (looksLikeHtml) {
    const status = raw.match(/Error code:\s*(\d+)/i)?.[1] || raw.match(/<p>Error code:\s*(\d+)<\/p>/i)?.[1];
    if (status === '404') return 'This data surface is not available from the current backend.';
    if (status === '501') return 'The current server does not support this request yet.';
    return fallback;
  }

  if (/timed out|failed to fetch|networkerror|load failed|request timeout/i.test(raw)) {
    return `${fallback} The public API demo may be waking up, so retry in a few seconds.`;
  }

  return raw
    .replace(/\s+/g, ' ')
    .replace(/`\/?v\d+\/api\/([^`]+)`/g, 'this data surface')
    .trim();
}
