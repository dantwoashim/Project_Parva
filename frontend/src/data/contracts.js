/**
 * Temporal Cartography frontend contracts (JSDoc typed shapes).
 */

/**
 * @typedef {Object} TemporalContextState
 * @property {string} date
 * @property {{latitude: number, longitude: number}} location
 * @property {string} timezone
 * @property {'observance'|'authority'} mode
 * @property {'en'|'ne'} language
 * @property {'computed'|'provisional'|'inventory'|'all'} qualityBand
 */

/**
 * @typedef {Object} GlossaryTerm
 * @property {string} name
 * @property {string} meaning
 * @property {string=} why_it_matters
 */

/**
 * @typedef {Object} CompassPayload
 * @property {string} date
 * @property {{year:number,month:number,day:number,month_name:string}} bikram_sambat
 * @property {{tithi_name:string,tithi_number:number,paksha:string,phase_ratio:number}} primary_readout
 * @property {{sunrise:string,sunset:string,current_muhurta:Object}} horizon
 * @property {{festivals:Array<Object>,count:number}} today
 */

/**
 * @typedef {Object} MuhurtaHeatBlock
 * @property {number} index
 * @property {string} start
 * @property {string} end
 * @property {'auspicious'|'neutral'|'avoid'} class
 * @property {number=} score
 * @property {Array<string>=} reason_codes
 */

/**
 * @typedef {Object} KundaliGraphPayload
 * @property {{viewbox:string,house_nodes:Array<Object>,graha_nodes:Array<Object>,aspect_edges:Array<Object>}} layout
 * @property {Array<{id:string,title:string,summary:string}>} insight_blocks
 */

export const CONTRACTS_VERSION = 'temporal-cartography-v2';
