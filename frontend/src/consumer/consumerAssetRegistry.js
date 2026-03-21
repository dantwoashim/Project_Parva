const FESTIVAL_ART_BY_ID = {
  dashain: 'mountain',
  diwali: 'lamp',
  tihar: 'lamp',
  holi: 'colors',
  pongal: 'harvest',
  chhath: 'harvest',
  indra_jatra: 'mandala',
  'indra-jatra': 'mandala',
  buddha_jayanti: 'moon',
  'buddha-jayanti': 'moon',
};

const FESTIVAL_ART_BY_CATEGORY = {
  national: 'lamp',
  hindu: 'lamp',
  newari: 'mandala',
  buddhist: 'moon',
  regional: 'harvest',
};

export function getConsumerFestivalArtKey(festivalId, category) {
  if (festivalId && FESTIVAL_ART_BY_ID[festivalId]) {
    return FESTIVAL_ART_BY_ID[festivalId];
  }

  if (category && FESTIVAL_ART_BY_CATEGORY[category]) {
    return FESTIVAL_ART_BY_CATEGORY[category];
  }

  return 'lamp';
}
