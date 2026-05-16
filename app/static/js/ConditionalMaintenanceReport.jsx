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
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    technicien: "", date: new Date().toISOString().split("T")[0],
    machine: "", machineSap: "", machineArea: "", compteur: "",
    typeIntervention: "preventive_300k",
    observations: "", signature: "",
  });
  const [checks, setChecks] = useState({
    demontage_bloc: null,
    nettoyage_tetes: null,
    lames_denudage_face_sup: null,
    lames_denudage_face_inf: null,
    lames_coupe: null,
    rondelle_isolante: null,
    entretoises_ceramique: null,
    serrage_vis: null,
    montage_bloc: null,
    verification_camera: null,
    photos_enregistrees: null,
    echantillons: null,
    controle_journalier: null,
  });
  const [submitted, setSubmitted] = useState(false);

  const setCheck = (key, val) => setChecks(c => ({ ...c, [key]: val }));
  const setField = (key, val) => setForm(f => ({ ...f, [key]: val }));

  const totalChecks = Object.values(checks).filter(v => v !== null).length;
  const allChecks = Object.keys(checks).length;
  const nokCount = Object.values(checks).filter(v => v === "NOK").length;
  const okCount = Object.values(checks).filter(v => v === "OK").length;
  const progress = Math.round((totalChecks / allChecks) * 100);

  const machineInfo = MACHINE_TYPES.find(m => m.value === form.machine);
  const isCC36 = form.machine === "cc36sp";
  const isSemiAuto = form.machine === "bt712_bt722_bt752";

  const steps = ["Identification", "Démontage & Vérification", "Montage & Validation", "Résumé"];

  if (submitted) {
    return (
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem" }}>
        <h2 className="sr-only">Rapport soumis avec succès</h2>
        <div style={{
          textAlign: "center", padding: "3rem 2rem",
          border: `0.5px solid ${COLORS.border}`,
          borderRadius: "var(--border-radius-lg)",
          background: "#fff"
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: "50%",
            background: COLORS.success,
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 1.5rem",
            boxShadow: `0 4px 12px rgba(45, 138, 78, 0.2)`
          }}>
            <i className="ti ti-check" style={{ fontSize: 32, color: "#fff", fontWeight: 700 }} />
          </div>
          <h2 style={{ margin: "0 0 8px", fontSize: 20, fontWeight: 700, color: COLORS.textPrimary }}>Rapport soumis avec succès</h2>
          <p style={{ color: COLORS.textSecondary, margin: "0 0 24px", fontWeight: 500 }}>
            Le rapport de maintenance a été enregistré pour <strong>{form.machine && machineInfo?.label}</strong>
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, margin: "0 0 28px"
          }}>
            {[
              { label: "Contrôles OK", val: okCount, color: COLORS.success },
              { label: "Contrôles NOK", val: nokCount, color: COLORS.danger },
              { label: "Total effectués", val: totalChecks, color: COLORS.primary },
            ].map(({ label, val, color }) => (
              <div key={label} style={{
                padding: "12px", background: COLORS.bg,
                borderRadius: "var(--border-radius-md)", border: `0.5px solid ${COLORS.border}`
              }}>
                <p style={{ margin: 0, fontSize: 22, fontWeight: 700, color }}>{val}</p>
                <p style={{ margin: 0, fontSize: 12, color: COLORS.textSecondary, fontWeight: 600 }}>{label}</p>
              </div>
            ))}
          </div>
          <button
            onClick={() => { setSubmitted(false); setStep(0); setForm(f => ({ ...f, technicien: "", machine: "", machineSap: "", compteur: "", observations: "" })); setChecks(Object.fromEntries(Object.keys(checks).map(k => [k, null]))); }}
            style={{ ...inputStyle, width: "auto", padding: "10px 28px", cursor: "pointer", background: COLORS.primary, color: "#fff", border: "none", fontWeight: 700, boxShadow: `0 2px 8px rgba(24, 95, 165, 0.2)` }}
          >
            Nouveau rapport
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "1.5rem 1rem", fontFamily: "var(--font-sans)" }}>
      <h2 className="sr-only">Rapport de maintenance préventive conditionnelle — Tête de coupe</h2>

      {/* Header */}
      <div style={{
        background: "#fff",
        border: `0.5px solid ${COLORS.border}`,
        borderRadius: "var(--border-radius-lg)", padding: "1.25rem 1.5rem",
        marginBottom: 20, borderLeft: `3px solid ${COLORS.primary}`
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
          <div>
            <p style={{ margin: 0, fontSize: 11, fontWeight: 700, color: COLORS.primary, textTransform: "uppercase", letterSpacing: "0.08em" }}>SEBN TN — Service Maintenance</p>
            <h1 style={{ margin: "4px 0 2px", fontSize: 18, fontWeight: 700, color: COLORS.textPrimary }}>
              Rapport de maintenance préventive conditionnelle
            </h1>
            <p style={{ margin: 0, fontSize: 13, color: COLORS.textSecondary }}>
              Entretien et ajustement — Tête de coupe dénudage
            </p>
          </div>
          <div style={{ textAlign: "right", flexShrink: 0 }}>
            <p style={{ margin: 0, fontSize: 11, color: COLORS.textSecondary }}>Réf. PPR-AA-TN</p>
            <p style={{ margin: "2px 0 0", fontSize: 11, color: COLORS.textSecondary }}>Fréquence: 300 000 coupes</p>
          </div>
        </div>
      </div>

      {/* Progress stepper */}
      <div style={{ display: "flex", alignItems: "center", marginBottom: 24, gap: 0 }}>
        {steps.map((s, i) => (
          <div key={s} style={{ display: "flex", alignItems: "center", flex: i < steps.length - 1 ? 1 : "none" }}>
            <div
              onClick={() => i < step && setStep(i)}
              style={{
                width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12, fontWeight: 700, cursor: i < step ? "pointer" : "default",
                background: i < step ? COLORS.success : i === step ? COLORS.primary : COLORS.bg,
                color: i <= step ? "#fff" : COLORS.textSecondary,
                border: i === step ? "none" : `0.5px solid ${COLORS.border}`,
                transition: "all 0.2s ease",
                boxShadow: i === step ? `0 2px 8px rgba(24, 95, 165, 0.2)` : "none"
              }}
            >
              {i < step ? <i className="ti ti-check" style={{ fontSize: 14 }} /> : i + 1}
            </div>
            <span style={{
              fontSize: 12, marginLeft: 6, color: i === step ? COLORS.textPrimary : COLORS.textSecondary,
              fontWeight: i === step ? 600 : 400, whiteSpace: "nowrap"
            }}>{s}</span>
            {i < steps.length - 1 && (
              <div style={{ flex: 1, height: 1, background: i < step ? COLORS.success : COLORS.border, margin: "0 8px" }} />
            )}
          </div>
        ))}
      </div>

      <div style={{
        background: "#fff",
        border: `0.5px solid ${COLORS.border}`,
        borderRadius: "var(--border-radius-lg)", padding: "1.5rem"
      }}>

        {/* ── STEP 0: Identification ── */}
        {step === 0 && (
          <div>
            <Section title="Informations générales" icon="clipboard-text" color="#185fa5">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <Field label="Technicien">
                  <input style={inputStyle} placeholder="Nom du technicien" value={form.technicien} onChange={e => setField("technicien", e.target.value)} />
                </Field>
                <Field label="Date d'intervention">
                  <input type="date" style={inputStyle} value={form.date} onChange={e => setField("date", e.target.value)} />
                </Field>
                <Field label="Type d'intervention">
                  <select style={inputStyle} value={form.typeIntervention} onChange={e => setField("typeIntervention", e.target.value)}>
                    <option value="preventive_300k">Préventive — 300 000 coupes</option>
                    <option value="hebdomadaire">Vérification hebdomadaire</option>
                    <option value="corrective">Corrective</option>
                  </select>
                </Field>
                <Field label="Type de machine">
                  <select style={inputStyle} value={form.machine} onChange={e => setField("machine", e.target.value)}>
                    <option value="">— Sélectionner —</option>
                    {MACHINE_TYPES.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </Field>
                <Field label="Machine SAP">
                  <input style={inputStyle} placeholder="Ex: 355-0310" value={form.machineSap} onChange={e => setField("machineSap", e.target.value)} />
                </Field>
                <Field label="Zone / Workstation">
                  <input style={inputStyle} placeholder="Ex: K355 — P1 Automat" value={form.machineArea} onChange={e => setField("machineArea", e.target.value)} />
                </Field>
                <Field label="Compteur de coupes (CAO)">
                  <input style={inputStyle} type="number" placeholder="Ex: 300000" value={form.compteur} onChange={e => setField("compteur", e.target.value)} />
                </Field>
              </div>
            </Section>

            {form.machine && (
              <div style={{
                padding: "12px 16px", borderRadius: "var(--border-radius-md)",
                background: "#E8F4F8", marginTop: 8,
                border: `0.5px solid #B3E5FC`
              }}>
                <p style={{ margin: 0, fontSize: 13, color: COLORS.primary, lineHeight: 1.6, fontWeight: 500 }}>
                  <i className="ti ti-info-circle" style={{ marginRight: 6, fontSize: 14 }} aria-hidden="true" />
                  <strong>Rappel :</strong> La vérification doit être effectuée tous les 300 000 coupes ou chaque semaine.
                  Durée estimée : <strong>20 minutes</strong>. La libération de machine doit être assurée par un chef d'équipe maintenance.
                  {(isCC36) && " Machine équipée ACD/SmartDetect — vérification déclenchée automatiquement."}
                </p>
              </div>
            )}
          </div>
        )}

        {/* ── STEP 1: Démontage & Vérification ── */}
        {step === 1 && (
          <div>
            <Section title="Démontage du bloc couteaux" icon="tool" color="#185fa5">
              <CheckRow
                label="Démontage du bloc couteaux"
                note="Démonter toutes les lames de dénudage et les lames de coupe"
                value={checks.demontage_bloc}
                onChange={v => setCheck("demontage_bloc", v)}
              />
              {!isCC36 && (
                <CheckRow
                  label="Nettoyage des têtes de coupe"
                  note="Nettoyer autour des lames. Ne pas utiliser d'air comprimé — alcool sur chiffon doux non pelucheux"
                  value={checks.nettoyage_tetes}
                  onChange={v => setCheck("nettoyage_tetes", v)}
                />
              )}
              {isCC36 && (
                <CheckRow
                  label="Nettoyage tête de coupe CC36 SP"
                  note="Nettoyer régulièrement les têtes, particulièrement autour des lames et des blocs. Alcool sur chiffon doux — pas d'air comprimé"
                  value={checks.nettoyage_tetes}
                  onChange={v => setCheck("nettoyage_tetes", v)}
                />
              )}
            </Section>

            <Section title="Vérification des lames (caméra USB)" icon="camera" color="#3B6D11">
              <div style={{
                padding: "10px 14px", borderRadius: "var(--border-radius-md)",
                background: COLORS.bg, marginBottom: 12, fontSize: 13,
                color: COLORS.textSecondary, lineHeight: 1.6
              }}>
                <i className="ti ti-alert-triangle" style={{ color: COLORS.warning, marginRight: 6 }} aria-hidden="true" />
                Vérifier l'état des lames à l'aide d'une caméra USB sur la <strong>partie opérative de la lame</strong>.
                {isSemiAuto && " Enregistrer 2 lames de dénudage et 3 échantillons sans sertissage."}
              </div>
              <CheckRow
                label="État lames de dénudage — face supérieure"
                note="Vérifier usure, ébréchures, déformations"
                value={checks.lames_denudage_face_sup}
                onChange={v => setCheck("lames_denudage_face_sup", v)}
                withPhoto
              />
              <CheckRow
                label="État lames de dénudage — face inférieure"
                note="Vérifier usure, ébréchures, déformations"
                value={checks.lames_denudage_face_inf}
                onChange={v => setCheck("lames_denudage_face_inf", v)}
                withPhoto
              />
              <CheckRow
                label="État lames de coupe"
                note="Vérifier usure et intégrité des tranchants"
                value={checks.lames_coupe}
                onChange={v => setCheck("lames_coupe", v)}
                withPhoto
              />
            </Section>

            {isCC36 && (
              <Section title="Vérification éléments SmartDetect (CC36 SP)" icon="cpu" color="#534AB7">
                <CheckRow
                  label="Rondelle isolante (jaune) — article 444 046"
                  note="Vérifier entre la vis et la lame. Aucun endommagement toléré — remplacement immédiat si NOK"
                  value={checks.rondelle_isolante}
                  onChange={v => setCheck("rondelle_isolante", v)}
                  withPhoto
                />
                <CheckRow
                  label="Entretoises en céramique blanche"
                  note="Vérifier l'intégrité entre les lames et le bloc. Aucun endommagement toléré"
                  value={checks.entretoises_ceramique}
                  onChange={v => setCheck("entretoises_ceramique", v)}
                  withPhoto
                />
                <div style={{
                  padding: "10px 14px", borderRadius: "var(--border-radius-md)",
                  background: "#FAECE7", marginTop: 4, fontSize: 13, color: "#4A1B0C", lineHeight: 1.6,
                  border: `0.5px solid #F0997B`
                }}>
                  <i className="ti ti-alert-circle" style={{ color: "#D85A30", marginRight: 6 }} aria-hidden="true" />
                  <strong>Attention :</strong> Les vis de fixation des lames de dénudage doivent être serrées à <strong>3 Nm</strong>.
                  Un serrage excessif peut casser la céramique sous la lame.
                </div>
              </Section>
            )}
          </div>
        )}

        {/* ── STEP 2: Montage & Validation ── */}
        {step === 2 && (
          <div>
            {isCC36 && (
              <Section title="Serrage et montage (CC36 SP)" icon="bolt" color="#534AB7">
                <CheckRow
                  label="Serrage des vis de fixation à 3 Nm"
                  note="Utiliser un tournevis dynamométrique — serrage excessif interdit"
                  value={checks.serrage_vis}
                  onChange={v => setCheck("serrage_vis", v)}
                />
              </Section>
            )}

            <Section title="Montage et remontage" icon="settings" color="#185fa5">
              <CheckRow
                label="Montage du bloc de lames"
                note="Remonter le bloc couteaux selon la procédure standard"
                value={checks.montage_bloc}
                onChange={v => setCheck("montage_bloc", v)}
              />
              <CheckRow
                label="Vérification fonctionnelle post-montage"
                note="Tester le cycle de dénudage et vérifier le bon fonctionnement"
                value={checks.verification_camera}
                onChange={v => setCheck("verification_camera", v)}
              />
            </Section>

            <Section title="Enregistrement et traçabilité" icon="folder" color="#3B6D11">
              <div style={{
                padding: "10px 14px", borderRadius: "var(--border-radius-md)",
                background: COLORS.bg, marginBottom: 12, fontSize: 13,
                color: COLORS.textSecondary, lineHeight: 1.6
              }}>
                Enregistrer les images dans le dossier réseau :{" "}
                <code style={{ fontSize: 12, background: "rgba(0,0,0,0.04)", padding: "2px 6px", borderRadius: 4, fontFamily: "monospace", color: COLORS.textPrimary }}>
                  Réseau &gt; 10.110.2.23 &gt; komax &gt; maintenance &gt; 01-bloc-de-lame
                </code>
              </div>
              <CheckRow
                label="Photos enregistrées dans le dossier réseau"
                note="Lames de dénudage + lames de coupe + 3 échantillons dénudage 2 côtés"
                value={checks.photos_enregistrees}
                onChange={v => setCheck("photos_enregistrees", v)}
              />
              <CheckRow
                label="Échantillons de dénudage réalisés et validés"
                note={isSemiAuto ? "3 échantillons sans sertissage, 2 lames de dénudage enregistrées" : "3 échantillons de dénudage 2 côtés"}
                value={checks.echantillons}
                onChange={v => setCheck("echantillons", v)}
              />
              {isSemiAuto && (
                <CheckRow
                  label="Contrôle journalier rempli"
                  note="Remplir le contrôle journalier de la machine semi-automatique"
                  value={checks.controle_journalier}
                  onChange={v => setCheck("controle_journalier", v)}
                />
              )}
            </Section>

            <Section title="Observations" icon="note" color="#888780">
              <textarea
                style={{ ...inputStyle, minHeight: 90, resize: "vertical" }}
                placeholder="Anomalies constatées, actions correctives réalisées, pièces remplacées…"
                value={form.observations}
                onChange={e => setField("observations", e.target.value)}
              />
            </Section>
          </div>
        )}

        {/* ── STEP 3: Résumé ── */}
        {step === 3 && (
          <div>
            <div style={{
              display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 20
            }}>
              {[
                { label: "Progression", val: `${progress}%`, color: COLORS.primary },
                { label: "Contrôles OK", val: okCount, color: COLORS.success },
                { label: "Contrôles NOK", val: nokCount, color: nokCount > 0 ? COLORS.danger : COLORS.textSecondary },
                { label: "Non renseignés", val: allChecks - totalChecks, color: allChecks - totalChecks > 0 ? COLORS.warning : COLORS.textSecondary },
              ].map(({ label, val, color }) => (
                <div key={label} style={{ padding: "12px 10px", background: COLORS.bg, borderRadius: "var(--border-radius-md)", textAlign: "center" }}>
                  <p style={{ margin: 0, fontSize: 22, fontWeight: 700, color }}>{val}</p>
                  <p style={{ margin: 0, fontSize: 11, color: COLORS.textSecondary, fontWeight: 600 }}>{label}</p>
                </div>
              ))}
            </div>

            <Section title="Récapitulatif de l'intervention" icon="list-check" color={COLORS.primary}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 13 }}>
                {[
                  ["Technicien", form.technicien || "—"],
                  ["Date", form.date],
                  ["Machine", machineInfo?.label || "—"],
                  ["SAP", form.machineSap || "—"],
                  ["Zone", form.machineArea || "—"],
                  ["Compteur", form.compteur ? `${Number(form.compteur).toLocaleString()} coupes` : "—"],
                ].map(([k, v]) => (
                  <div key={k} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "7px 10px", background: COLORS.bg,
                    borderRadius: "var(--border-radius-md)"
                  }}>
                    <span style={{ color: COLORS.textSecondary, fontWeight: 600 }}>{k}</span>
                    <span style={{ fontWeight: 700, color: COLORS.textPrimary }}>{v}</span>
                  </div>
                ))}
              </div>
            </Section>

            {nokCount > 0 && (
              <div style={{
                padding: "12px 16px", borderRadius: "var(--border-radius-md)",
                background: "#FCEBEB", border: `0.5px solid #F09595`, marginBottom: 16
              }}>
                <p style={{ margin: 0, fontSize: 13, color: COLORS.danger, fontWeight: 700 }}>
                  <i className="ti ti-alert-circle" style={{ marginRight: 6 }} aria-hidden="true" />
                  {nokCount} contrôle{nokCount > 1 ? "s" : ""} NOK détecté{nokCount > 1 ? "s" : ""} — action corrective requise avant libération machine.
                </p>
              </div>
            )}

            <Section title="Validation et signature" icon="signature" color="#3B6D11">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <Field label="Nom du signataire (chef d'équipe)">
                  <input style={inputStyle} placeholder="Nom et prénom" value={form.signature} onChange={e => setField("signature", e.target.value)} />
                </Field>
                <Field label="Date de validation">
                  <input type="date" style={inputStyle} value={form.date} readOnly />
                </Field>
              </div>
              <div style={{
                marginTop: 12, padding: "10px 14px", borderRadius: "var(--border-radius-md)",
                background: "#E8F4F8", border: `0.5px solid #B3E5FC`,
                fontSize: 13, color: COLORS.primary
              }}>
                <i className="ti ti-info-circle" style={{ marginRight: 6 }} aria-hidden="true" />
                La libération de la machine doit être assurée par un chef d'équipe maintenance après vérification que la tâche est effectuée convenablement.
              </div>
            </Section>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16, gap: 12 }}>
        <button
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0}
          style={{
            ...inputStyle, width: "auto", padding: "9px 20px", cursor: step === 0 ? "not-allowed" : "pointer",
            opacity: step === 0 ? 0.4 : 1, display: "flex", alignItems: "center", gap: 6,
            background: "#fff", color: COLORS.textPrimary, fontWeight: 700, border: `1px solid ${COLORS.border}`
          }}
        >
          <i className="ti ti-arrow-left" style={{ fontSize: 14 }} aria-hidden="true" />
          Précédent
        </button>

        <span style={{ fontSize: 12, color: COLORS.textSecondary, fontWeight: 700 }}>
          Étape {step + 1} / {steps.length}
        </span>

        {step < steps.length - 1 ? (
          <button
            onClick={() => setStep(s => Math.min(steps.length - 1, s + 1))}
            style={{
              ...inputStyle, width: "auto", padding: "9px 20px", cursor: "pointer",
              background: COLORS.primary, color: "#fff", border: "none", fontWeight: 700,
              display: "flex", alignItems: "center", gap: 6, boxShadow: `0 2px 8px rgba(24, 95, 165, 0.2)`
            }}
          >
            Suivant
            <i className="ti ti-arrow-right" style={{ fontSize: 14 }} aria-hidden="true" />
          </button>
        ) : (
          <button
            onClick={() => setSubmitted(true)}
            disabled={!form.technicien || !form.machine}
            style={{
              ...inputStyle, width: "auto", padding: "9px 20px",
              cursor: (!form.technicien || !form.machine) ? "not-allowed" : "pointer",
              background: (!form.technicien || !form.machine) ? COLORS.textSecondary : COLORS.success,
              color: "#fff",
              border: "none", fontWeight: 700, display: "flex", alignItems: "center", gap: 6,
              opacity: (!form.technicien || !form.machine) ? 0.6 : 1,
              boxShadow: (!form.technicien || !form.machine) ? "none" : `0 2px 8px rgba(45, 138, 78, 0.2)`
            }}
          >
            <i className="ti ti-check" style={{ fontSize: 14 }} aria-hidden="true" />
            Soumettre le rapport
          </button>
        )}
      </div>
    </div>
  );
}
