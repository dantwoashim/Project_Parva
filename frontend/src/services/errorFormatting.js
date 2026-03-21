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
    return error.trim();
  }

  const message = typeof error?.message === 'string' && error.message.trim()
    ? error.message.trim()
    : fallback;
  const requestId = normalizeRequestId(error);
  if (!requestId) {
    return message;
  }
  return `${message} Support reference: ${requestId}.`;
}

export function pickRejectedReason(...results) {
  return results.find((result) => result?.status === 'rejected')?.reason ?? null;
}
