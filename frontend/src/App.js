/**
 * THERMALIS-X Main Application Entrypoint
 */
import { MapViewer } from './components/MapViewer.js';
import { AnalyticsDrawer } from './components/AnalyticsDrawer.js';
import { ReplayEngine } from './components/ReplayEngine.js';
import { fetchEvents, fetchFacilities, fetchAlerts } from './services/api.js';

console.log('THERMALIS-X GIS Command Console Initialized');
