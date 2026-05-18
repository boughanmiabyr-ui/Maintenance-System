import { useState } from "react";

// Professional color palette - consistent with Flask template
const COLORS = {
  primary: "#185fa5",
  success: "#2d8a4e",
  danger: "#c0392b",
  warning: "#BA7517",
  neutral: "#888780",
  textPrimary: "#2c3e50",
  textSecondary: "#7f8c8d",
  border: "#ecf0f1",
  bg: "#f8f9fa",
};

const CRITICALITY = { low: "Basse", medium: "Moyenne", high: "Haute", critical: "Critique" };

// Inject CSS custom properties for consistency
const cssVariables = `
  :root {
    --color-primary: ${COLORS.primary};
    --color-success: ${COLORS.success};
    --color-danger: ${COLORS.danger};
    --color-warning: ${COLORS.warning};
    --color-neutral: ${COLORS.neutral};
    --color-text-primary: ${COLORS.textPrimary};
    --color-text-secondary: ${COLORS.textSecondary};
    --color-border: ${COLORS.border};
    --color-border-secondary: ${COLORS.border};
    --color-border-tertiary: ${COLORS.border};
    --color-background-primary: white;
    --color-background-secondary: ${COLORS.bg};
    --color-background-tertiary: ${COLORS.bg};
    --color-background-success: ${COLORS.success};
    --color-background-info: #E8F4F8;
    --color-text-info: #185fa5;
    --color-border-info: #B3E5FC;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;
    --font-sans: system-ui, -apple-system, sans-serif;
  }
`;

// Create and inject style element
if (typeof document !== 'undefined') {
  const styleEl = document.createElement('style');
  styleEl.textContent = cssVariables;
  document.head.appendChild(styleEl);
}

const MACHINE_TYPES = [
  { value: "komax355_segma688_alpha550", label: "KOMAX 355 / SEGMA688 / ALPHA 550 UTP" },
  { value: "ps9550_ps9580_ulmer", label: "PS9550 / PS9580 / ULMER" },
  { value: "bt712_bt722_bt752", label: "BT 712 / BT722 / BT752 (Semi-auto)" },
  { value: "cc36sp", label: "CC36 SP (avec ACD/SmartDetect)" },
];

const STATUS = { OK: "OK", NOK: "NOK", NA: "N/A" };

const StatusBtn = ({ value, current, onChange }) => {
  const styles = {
    OK: { bg: value === current ? COLORS.success : "transparent", color: value === current ? "#fff" : COLORS.success, border: `1.5px solid ${COLORS.success}` },
    NOK: { bg: value === current ? COLORS.danger : "transparent", color: value === current ? "#fff" : COLORS.danger, border: `1.5px solid ${COLORS.danger}` },
    "N/A": { bg: value === current ? COLORS.neutral : "transparent", color: value === current ? "#fff" : COLORS.neutral, border: `1.5px solid ${COLORS.neutral}` },
  };
  return (
    <button
      onClick={() => onChange(value)}
      style={{
        padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: 500,
        cursor: "pointer", transition: "all 0.15s", ...styles[value]
      }}
    >
      {value}
    </button>
  );
};

const CheckRow = ({ label, note, value, onChange, withPhoto }) => (
  <div style={{
    display: "grid", gridTemplateColumns: "1fr auto auto", gap: 12,
    alignItems: "center", padding: "10px 0",
    borderBottom: `0.5px solid ${COLORS.border}`
  }}>
    <div>
      <p style={{ margin: 0, fontSize: 14, color: COLORS.textPrimary, lineHeight: 1.5, fontWeight: 500 }}>{label}</p>
      {note && <p style={{ margin: "2px 0 0", fontSize: 12, color: COLORS.textSecondary }}>{note}</p>}
    </div>
    {withPhoto && (
      <label style={{
        fontSize: 11, color: COLORS.primary, cursor: "pointer",
        border: `0.5px solid ${COLORS.primary}`, borderRadius: 6,
        padding: "4px 8px", whiteSpace: "nowrap", transition: "all 0.2s"
      }}>
        <i className="ti ti-camera" style={{ marginRight: 4, fontSize: 12 }} />
        Photo
        <input type="file" accept="image/*" style={{ display: "none" }} />
      </label>
    )}
    <div style={{ display: "flex", gap: 6 }}>
      {Object.values(STATUS).map(s => (
        <StatusBtn key={s} value={s} current={value} onChange={onChange} />
      ))}
    </div>
  </div>
);

const Section = ({ title, icon, children, color = COLORS.primary }) => (
  <div style={{ marginBottom: 24 }}>
    <div style={{
      display: "flex", alignItems: "center", gap: 8, marginBottom: 12,
      paddingBottom: 8, borderBottom: `2px solid ${color}`
    }}>
      <i className={`ti ti-${icon}`} style={{ fontSize: 18, color, fontWeight: 600 }} />
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: COLORS.textPrimary, letterSpacing: "-0.3px" }}>{title}</h3>
    </div>
    {children}
  </div>
);

const Field = ({ label, children }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
    <label style={{ 
      fontSize: 11, 
      fontWeight: 700, 
      color: COLORS.textSecondary, 
      textTransform: "uppercase", 
      letterSpacing: "0.05em"
    }}>
      {label}
    </label>
    {children}
  </div>
);

const inputStyle = {
  padding: "8px 10px", borderRadius: 8, fontSize: 14,
  border: `0.5px solid ${COLORS.border}`,
  background: COLORS.bg,
  color: COLORS.textPrimary, width: "100%", boxSizing: "border-box"
};

export default function App() {
  // Get pre-selected data from data attributes or global variables
  const containerEl = typeof document !== 'undefined' ? document.currentScript?.parentElement : null;
  const preSelectedTechnician = containerEl?.dataset?.technicianName || window.__conditionalReport?.technicianName || "";
  const preSelectedMachine = containerEl?.dataset?.machineName || window.__conditionalReport?.machineName || "";
  const preSelectedZone = containerEl?.dataset?.zone || window.__conditionalReport?.zone || "";

  // Auto-generate today's date (non-editable)
  const todayDate = new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '/');
  
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    technician: preSelectedTechnician,
    date: todayDate,
    machine: preSelectedMachine,
    zone: preSelectedZone
  });

  const checkItems = [
    { id: 1, label: "Machine propre", note: "État de la propreté générale" },
    { id: 2, label: "Absence d'anomalies visuelles", note: "Vérifier fuites, fissures, corrosion" },
    { id: 3, label: "Vibrations anormales", note: "Écouter et ressentir pendant fonctionnement" },
    { id: 4, label: "Bruits anormaux", note: "Grincements, cliquetis, sifflements" },
    { id: 5, label: "Résidus de coupe présents", note: "Vérifier accumulation de débris" },
    { id: 6, label: "État général des lames", note: "Aspect, brillance, déformations" },
    { id: 7, label: "Usure des lames", note: "Vérifier uniformité et progression" },
    { id: 8, label: "Absence de fissures", note: "Inspectez la surface entière" },
    { id: 9, label: "Absence d'ébréchures", note: "Vérifier les arêtes et tranchants" },
    { id: 10, label: "Alignement des lames", note: "Vérifier parallélisme et positionnement" },
    { id: 11, label: "Absence de déformations", note: "Vérifier planéité et rectitude" },
    { id: 12, label: "Vérification caméra effectuée", note: "Inspection détaillée avec caméra USB" },
    { id: 13, label: "État des arêtes de coupe", note: "Partie opérative des lames" },
    { id: 14, label: "Position des couteaux", note: "Vérifier écartement et positionnement" },
    { id: 15, label: "Mouvement vertical", note: "Course et fluidité du mouvement" },
    { id: 16, label: "Qualité du dénudage", note: "Uniformité et propreté" },
    { id: 17, label: "Évacuation des résidus", note: "Absence de blocage ou accumulation" },
    { id: 18, label: "État du mécanisme", note: "Fluide, sans blocage" },
    { id: 19, label: "Montage du bloc lame", note: "Fixation et stabilité" },
    { id: 20, label: "État du serrage", note: "Vis et boulons correctement serrés" },
    { id: 21, label: "Absence de jeu mécanique", note: "Vérifier rigidité du bloc" },
    { id: 22, label: "Positionnement des composants", note: "Alignement et positionnement corrects" },
    { id: 23, label: "Test fonctionnel", note: "Fonctionnement sans à-coups" },
    { id: 24, label: "Nettoyage effectué", note: "Machine complètement nettoyée" },
    { id: 25, label: "Zone sécurisée", note: "Aucun débris ou objet traînant" },
    { id: 26, label: "Résidus évacués", note: "Tous les débris collectés" },
    { id: 27, label: "Machine opérationnelle", note: "Prêt pour la production" },
    { id: 28, label: "Anomalies détectées", note: "Vérifier anomalies générales" },
  ];

  const [checks, setChecks] = useState(
    Object.fromEntries(checkItems.map(item => [item.id, ""]))
  );

  const [remarks, setRemarks] = useState(
    Object.fromEntries(checkItems.map(item => [item.id, ""]))
  );

  const handleSetCheck = (id, value) => {
    setChecks(prev => ({ ...prev, [id]: value }));
  };

  const handleSetRemark = (id, value) => {
    setRemarks(prev => ({ ...prev, [id]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Rapport soumis avec succès!");
  };

  const handleNextStep = () => {
    if (step < 1) {
      setStep(step + 1);
    }
  };

  const handlePrevStep = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  return (
    <div style={{ fontFamily: "var(--font-sans)", background: COLORS.bg, minHeight: "100vh", paddingBottom: "2rem" }}>
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "1.5rem 1rem" }}>
        <form onSubmit={handleSubmit}>
          {/* Header Card */}
          <div style={{
            background: "#fff",
            border: `0.5px solid ${COLORS.border}`,
            borderRadius: "var(--border-radius-lg)", 
            padding: "1.25rem 1.5rem",
            marginBottom: 24, 
            borderLeft: `3px solid ${COLORS.primary}`
          }}>
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
              <div>
                <p style={{ margin: 0, fontSize: 11, fontWeight: 700, color: COLORS.primary, textTransform: "uppercase", letterSpacing: "0.08em" }}>SEBN TN — Service Maintenance</p>
                <h1 style={{ margin: "4px 0 2px", fontSize: 20, fontWeight: 700, color: COLORS.textPrimary }}>
                  Rapport de maintenance préventive conditionnelle
                </h1>
                <p style={{ margin: 0, fontSize: 13, color: COLORS.textSecondary }}>
                  Inspection basée sur l'état machine
                </p>
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <p style={{ margin: 0, fontSize: 11, color: COLORS.textSecondary }}>Réf. PMC-AA-TN</p>
              </div>
            </div>
          </div>

          {/* Content Card */}
          <div style={{
            background: "#fff",
            border: `0.5px solid ${COLORS.border}`,
            borderRadius: "var(--border-radius-lg)", 
            padding: "1.5rem"
          }}>
            {/* STEP 0: General Information */}
            {step === 0 && (
              <div>
                <h2 style={{ margin: "0 0 1.5rem", fontSize: 18, fontWeight: 700, color: COLORS.textPrimary, paddingBottom: "12px", borderBottom: `2px solid ${COLORS.primary}` }}>
                  Informations générales
                </h2>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
                  {/* Technician */}
                  <div>
                    <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: COLORS.textSecondary, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Technicien *</label>
                    <input 
                      type="text"
                      value={form.technician}
                      readOnly
                      style={{
                        width: "100%", padding: "10px 12px", fontSize: 14, fontWeight: 500,
                        border: `1px solid ${COLORS.border}`, borderRadius: 8, background: COLORS.bg,
                        color: COLORS.textPrimary, cursor: "default"
                      }}
                    />
                  </div>

                  {/* Date */}
                  <div>
                    <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: COLORS.textSecondary, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Date d'intervention *</label>
                    <div style={{ position: "relative" }}>
                      <input 
                        type="text"
                        value={form.date}
                        readOnly
                        style={{
                          width: "100%", padding: "10px 12px", fontSize: 14, fontWeight: 500,
                          border: `1px solid ${COLORS.border}`, borderRadius: 8, background: COLORS.bg,
                          color: COLORS.textPrimary, cursor: "default", paddingRight: 40
                        }}
                      />
                      <i className="ti ti-calendar" style={{
                        position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                        fontSize: 18, color: COLORS.textSecondary, pointerEvents: "none"
                      }} />
                    </div>
                  </div>

                  {/* Machine Type */}
                  <div>
                    <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: COLORS.textSecondary, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Type de machine *</label>
                    <select 
                      value={form.machine}
                      readOnly
                      style={{
                        width: "100%", padding: "10px 12px", fontSize: 14, fontWeight: 500,
                        border: `1px solid ${COLORS.border}`, borderRadius: 8, background: COLORS.bg,
                        color: COLORS.textPrimary, cursor: "default"
                      }}
                    >
                      <option value="">— Sélectionner —</option>
                      <option value={form.machine}>{form.machine}</option>
                    </select>
                  </div>

                  {/* Zone */}
                  <div>
                    <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: COLORS.textSecondary, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Zone / Workstation</label>
                    <input 
                      type="text"
                      value={form.zone}
                      readOnly
                      style={{
                        width: "100%", padding: "10px 12px", fontSize: 14, fontWeight: 500,
                        border: `1px solid ${COLORS.border}`, borderRadius: 8, background: COLORS.bg,
                        color: COLORS.textPrimary, cursor: "default"
                      }}
                    />
                  </div>
                </div>

                {/* Next Button */}
                <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
                  <button
                    type="button"
                    onClick={handleNextStep}
                    style={{
                      padding: "10px 24px", fontSize: 14, fontWeight: 700, borderRadius: 8,
                      cursor: "pointer", background: COLORS.primary, color: "white",
                      border: "none", transition: "all 0.2s", display: "flex", alignItems: "center", gap: 6
                    }}
                  >
                    Suivant
                    <i className="ti ti-arrow-right" style={{ fontSize: 14 }} />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 1: Inspection Items */}
            {step === 1 && (
              <div>
                <h2 style={{ margin: "0 0 1.5rem", fontSize: 18, fontWeight: 700, color: COLORS.textPrimary, paddingBottom: "12px", borderBottom: `2px solid ${COLORS.primary}` }}>
                  État général de la machine
                </h2>

                <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 24 }}>
                  {checkItems.map((item) => (
                    <div 
                      key={item.id}
                      style={{
                        padding: "12px 0", borderBottom: `1px solid ${COLORS.border}`,
                        display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <p style={{ margin: "0 0 4px", fontSize: 14, fontWeight: 600, color: COLORS.textPrimary }}>
                          {item.label}
                        </p>
                        <p style={{ margin: 0, fontSize: 12, color: COLORS.textSecondary }}>
                          {item.note}
                        </p>
                      </div>
                      <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                        <button
                          type="button"
                          onClick={() => handleSetCheck(item.id, "OK")}
                          style={{
                            padding: "6px 14px", fontSize: 12, fontWeight: 600, borderRadius: 6,
                            cursor: "pointer", transition: "all 0.15s",
                            background: checks[item.id] === "OK" ? COLORS.success : "transparent",
                            color: checks[item.id] === "OK" ? "white" : COLORS.success,
                            border: `1.5px solid ${COLORS.success}`
                          }}
                        >
                          OK
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSetCheck(item.id, "NOK")}
                          style={{
                            padding: "6px 14px", fontSize: 12, fontWeight: 600, borderRadius: 6,
                            cursor: "pointer", transition: "all 0.15s",
                            background: checks[item.id] === "NOK" ? COLORS.danger : "transparent",
                            color: checks[item.id] === "NOK" ? "white" : COLORS.danger,
                            border: `1.5px solid ${COLORS.danger}`
                          }}
                        >
                          NOK
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSetCheck(item.id, "N/A")}
                          style={{
                            padding: "6px 14px", fontSize: 12, fontWeight: 600, borderRadius: 6,
                            cursor: "pointer", transition: "all 0.15s",
                            background: checks[item.id] === "N/A" ? COLORS.neutral : "transparent",
                            color: checks[item.id] === "N/A" ? "white" : COLORS.neutral,
                            border: `1.5px solid ${COLORS.neutral}`
                          }}
                        >
                          N/A
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Navigation Buttons */}
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                  <button
                    type="button"
                    onClick={handlePrevStep}
                    style={{
                      padding: "10px 24px", fontSize: 14, fontWeight: 700, borderRadius: 8,
                      cursor: "pointer", background: "white", color: COLORS.textPrimary,
                      border: `1px solid ${COLORS.border}`, transition: "all 0.2s", display: "flex", alignItems: "center", gap: 6
                    }}
                  >
                    <i className="ti ti-arrow-left" style={{ fontSize: 14 }} />
                    Précédent
                  </button>
                  <button
                    type="submit"
                    style={{
                      padding: "10px 24px", fontSize: 14, fontWeight: 700, borderRadius: 8,
                      cursor: "pointer", background: COLORS.success, color: "white",
                      border: "none", transition: "all 0.2s", display: "flex", alignItems: "center", gap: 6
                    }}
                  >
                    <i className="ti ti-check" style={{ fontSize: 14 }} />
                    Soumettre le rapport
                  </button>
                </div>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
