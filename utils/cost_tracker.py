from datetime import datetime, date
from typing import Dict, List
from dataclasses import dataclass, field
import json
import os

MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "local": {"input": 0.0, "output": 0.0},
    "ollama": {"input": 0.0, "output": 0.0},
}

@dataclass
class UsageRecord:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    task_preview: str = ""

@dataclass
class CostTracker:
    daily_budget: float = 2.0
    records: List[UsageRecord] = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    session_cost: float = 0.0

    def _get_pricing(self, model: str) -> Dict[str, float]:
        model_lower = model.lower()
        for key, price in MODEL_PRICING.items():
            if key in model_lower:
                return price
        return {"input": 0.50, "output": 1.50}

    def add_usage(self, model: str, input_tokens: int, output_tokens: int, task_preview: str = "") -> float:
        pricing = self._get_pricing(model)
        cost = (input_tokens / 1_000_000 * pricing["input"]) + (output_tokens / 1_000_000 * pricing["output"])
        
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost, 6),
            task_preview=task_preview[:80]
        )
        
        self.records.append(record)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        self.session_cost += cost
        return cost

    def get_today_cost(self) -> float:
        today = date.today().isoformat()
        return sum(r.cost_usd for r in self.records if r.timestamp.startswith(today))

    def is_budget_exceeded(self) -> bool:
        return self.get_today_cost() >= self.daily_budget

    def remaining_budget(self) -> float:
        return max(0.0, self.daily_budget - self.get_today_cost())

    def get_summary(self) -> Dict:
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "session_cost_usd": round(self.session_cost, 4),
            "today_cost_usd": round(self.get_today_cost(), 4),
            "remaining_budget_usd": round(self.remaining_budget(), 4),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "records_count": len(self.records),
            "budget_exceeded": self.is_budget_exceeded()
        }

tracker = CostTracker()
