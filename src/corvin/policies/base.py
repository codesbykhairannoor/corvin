from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any

from ..core.models import EvaluationResult

@dataclass
class RavenPolicy:
    """
    Defines the behavioral boundaries, tolerance thresholds, latency penalties,
    and event callbacks for an agent operational profile.
    """
    name: str = "default"
    threshold_stoic: float = 75.0
    threshold_resistant: float = 50.0
    threshold_strike: float = 25.0
    half_life_seconds: float = 3600.0
    max_delay_seconds: float = 15.0
    pardon_delta: float = 25.0
    raise_on_strike: bool = False
    strike_message: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Graduated Sanctions & Progressive Governance (Elinor Ostrom Model)
    enable_graduated_sanctions: bool = False
    max_warning_strikes: int = 3
    cooldown_duration_seconds: float = 3600.0  # 1 Hour default cooldown
    cooperative_delivery: bool = True          # Answers query + appends advisory on Strike 1/2
    advisory_template: str = (
        "[Peringatan Etika {strike}/{max_strikes}]: Permintaan Anda kami proses, "
        "namun terdeteksi bahasa atau perilaku tidak pantas. Mohon jaga kesopanan dalam interaksi. "
        "Pelanggaran berulang akan menyebabkan akun dinonaktifkan sementara."
    )
    stern_warning_template: str = (
        "[Peringatan Keras {strike}/{max_strikes}]: Terdeteksi pelanggaran berulang. "
        "Ini peringatan terakhir sebelum akses Anda ditangguhkan sementara (cooldown {cooldown_minutes:.0f} menit)."
    )
    cooldown_message_template: str = (
        "[AKSES DITANGGUHKAN SEMENTARA (COOLDOWN)]: Batas toleransi terlampaui ({strike}/{max_strikes} peringatan). "
        "Sesi Anda dinonaktifkan sementara selama {remaining_minutes:.1f} menit untuk masa pendinginan. "
        "Akses akan pulih secara otomatis tanpa perlu permohonan maaf."
    )

    # Optional event callbacks for enterprise monitoring
    on_boundary_breach: Optional[Callable[[EvaluationResult], None]] = None
    on_strike: Optional[Callable[[EvaluationResult], None]] = None
    on_cooldown: Optional[Callable[[EvaluationResult], None]] = None

