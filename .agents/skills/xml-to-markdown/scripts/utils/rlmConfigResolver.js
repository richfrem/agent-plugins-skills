import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Project Root is 3 levels up from tools/investigate/utils
// Project Root is 4 levels up from plugins/xml-to-markdown/scripts/utils
const PROJECT_ROOT = path.resolve(__dirname, '../../../../');
const FACTORY_INDEX_PATH = path.join(PROJECT_ROOT, 'tools', 'standalone', 'rlm-factory', 'manifest-index.json');

/**
 * Resolve the RLM Cache Path for a given type.
 * @param {string} type - 'legacy' or 'tool'
 * @returns {string} Absolute path to the RLM Cache file
 */
export function getRLMCachePath(type = 'legacy') {
    if (!fs.existsSync(FACTORY_INDEX_PATH)) {
        console.warn(`⚠️ Factory Index not found at ${FACTORY_INDEX_PATH}. Using default legacy path.`);
        return path.join(PROJECT_ROOT, '.agent/learning/rlm_summary_cache.json');
    }

    try {
        const data = fs.readFileSync(FACTORY_INDEX_PATH, 'utf-8');
        const index = JSON.parse(data);
        const config = index[type];

        if (!config || !config.cache) {
            console.warn(`⚠️ Unknown RLM Type or missing cache config: '${type}'. Using default.`);
            return path.join(PROJECT_ROOT, '.agent/learning/rlm_summary_cache.json');
        }

        // Cache path in manifest is relative to PROJECT_ROOT (usually)
        // Check rlm_config.py logic: cache_path = PROJECT_ROOT / cache_path_raw
        return path.resolve(PROJECT_ROOT, config.cache);

    } catch (e) {
        console.error(`❌ Error reading Factory Index: ${e.message}`);
        return path.join(PROJECT_ROOT, '.agent/learning/rlm_summary_cache.json');
    }
}
