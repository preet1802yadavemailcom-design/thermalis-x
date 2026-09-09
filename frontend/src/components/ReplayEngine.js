/**
 * THERMALIS-X Historical Replay Sequencer
 */
import { fetchReplaySteps } from '../services/api.js';

export class ReplayEngine {
  constructor(onStepChangeCallback) {
    this.currentCaseId = null;
    this.steps = [];
    this.currentIndex = 0;
    this.onStepChange = onStepChangeCallback;
  }

  async loadCase(caseId) {
    this.currentCaseId = caseId;
    this.steps = await fetchReplaySteps(caseId);
    this.currentIndex = 0;
    if (this.steps.length > 0) {
      this.onStepChange(this.steps[0], 0, this.steps.length);
    }
  }

  next() {
    if (this.currentIndex < this.steps.length - 1) {
      this.currentIndex++;
      this.onStepChange(this.steps[this.currentIndex], this.currentIndex, this.steps.length);
    }
  }

  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.onStepChange(this.steps[this.currentIndex], this.currentIndex, this.steps.length);
    }
  }
}
