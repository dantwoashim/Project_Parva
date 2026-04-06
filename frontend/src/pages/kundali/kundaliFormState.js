export function titleCase(value) {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function buildBirthDateIso(form) {
  const year = Number(form.birthYear);
  const month = Number(form.birthMonth);
  const day = Number(form.birthDay);
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) return null;
  const date = new Date(Date.UTC(year, month - 1, day));
  if (
    Number.isNaN(date.valueOf())
    || date.getUTCFullYear() !== year
    || date.getUTCMonth() !== month - 1
    || date.getUTCDate() !== day
  ) {
    return null;
  }
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

export function resolveBirthInput(form) {
  const birthDate = buildBirthDateIso(form);
  const errors = [];

  if (!birthDate) {
    errors.push('Enter a valid birth date.');
  }
  if (!/^\d{2}:\d{2}$/.test(form.birthTime || '')) {
    errors.push('Enter an exact birth time.');
  }

  const latitude = Number(form.latitude);
  const longitude = Number(form.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    errors.push('Select a birth place or enter valid coordinates.');
  }
  if (!String(form.timezone || '').trim()) {
    errors.push('Choose a timezone for the birth place.');
  }
  if (!String(form.placeQuery || '').trim()) {
    errors.push('Search and select a birth place.');
  }

  if (errors.length) {
    return {
      errors,
      value: null,
    };
  }

  return {
    errors: [],
    value: {
      date: birthDate,
      time: form.birthTime,
      datetime: `${birthDate}T${form.birthTime}:00`,
      latitude,
      longitude,
      timezone: form.timezone.trim(),
      placeLabel: form.placeQuery.trim(),
    },
  };
}

export function buildSavedReading(resolvedInput, payload) {
  return {
    id: `kundali:${resolvedInput.datetime}:${resolvedInput.latitude}:${resolvedInput.longitude}:${resolvedInput.timezone}`,
    title: `Birth reading | ${resolvedInput.placeLabel}`,
    datetime: resolvedInput.datetime,
    placeLabel: resolvedInput.placeLabel,
    location: {
      latitude: resolvedInput.latitude,
      longitude: resolvedInput.longitude,
      timezone: resolvedInput.timezone,
    },
    lagna: payload?.lagna?.rashi_english || null,
    moon: payload?.grahas?.moon?.rashi_english || null,
    createdAt: new Date().toISOString(),
  };
}
