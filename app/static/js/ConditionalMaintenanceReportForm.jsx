import { useState } from "react";

const MACHINE_TYPES = [
  { value: "komax355_segma688_alpha550", label: "KOMAX 355 / SEGMA688 / ALPHA 550 UTP" },
  { value: "ps9550_ps9580_ulmer", label: "PS9550 / PS9580 / ULMER" },
  { value: "bt712_bt722_bt752", label: "BT 712 / BT722 / BT752 (Semi-auto)" },
  { value: "cc36sp", label: "CC36 SP (avec ACD/SmartDetect)" },
];

const STATUS = { OK: "OK", NOK: "NOK", NA: "N/A" };
const ACTION_TYPES = { reset: "Réinitialisation compteur", replace: "Remplacement composants" };

const StatusBtn = ({ value, current, onChange }) => {
  const styles = {
    OK: { bg: value === current ? "#2d8a4e" : "transparent", color: value === current ? "#fff" : "#2d8a4e", border: "1.5px solid #2d8a4e" },
    NOK: { bg: value === current ? "#c0392b" : "transparent", color: value === current ? "#fff" : "#c0392b", border: "1.5px solid #c0392b" },
    "N/A": { bg: value === current ? "#888780" : "transparent", color: value === current ? "#fff" : "#888780", border: "1.5px solid #888780" },
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
    borderBottom: "0.5px solid var(--color-border-tertiary)"
  }}>
    <div>
      <p style={{ margin: 0, fontSize: 14, color: "var(--color-text-primary)", lineHeight: 1.5 }}>{label}</p>
      {note && <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--color-text-secondary)" }}>{note}</p>}
    </div>
    {withPhoto && (
      <label style={{
        fontSize: 11, color: "var(--color-text-info)", cursor: "pointer",
        border: "0.5px solid var(--color-border-info)", borderRadius: 6,
        padding: "4px 8px", whiteSpace: "nowrap"
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

const Section = ({ title, icon, children, color = "#185fa5" }) => (
  <div style={{ marginBottom: 24 }}>
    <div style={{
      display: "flex", alignItems: "center", gap: 8, marginBottom: 12,
      paddingBottom: 8, borderBottom: `2px solid ${color}`
    }}>
      <i className={`ti ti-${icon}`} style={{ fontSize: 18, color }} />
      <h3 style={{ margin: 0, fontSize: 16, fontWeight: 500, color }}>{title}</h3>
    </div>
    {children}
  </div>
);

const Field = ({ label, children }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
    <label style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</label>
    {children}
  </div>
);

const inputStyle = {
  padding: "8px 10px", borderRadius: 8, fontSize: 14,
  border: "0.5px solid var(--color-border-secondary)",
  background: "var(--color-background-secondary)",
  color: "var(--color-text-primary)", width: "100%", boxSizing: "border-box"
};

export default function App() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    technicien: "", date: new Date().toISOString().split("T")[0],
    machine: "", machineSap: "", machineArea: "", compteur: "",
    actionType: "reset",
    observations: "", signature: "", componentsReplaced: ""
  });
  const [checks, setChecks] = useState({
    compteur_verification: null,
    etat_machine_initial: null,
    inspection_composants: null,
    nettoyage_verification: null,
    fonctionnement_teste: null,
    documentation_complete: null,
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

  const steps = ["Identification", "Vérification & Inspection", "Actions & Validation", "Résumé"];

  if (submitted) {
    return (
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem" }}>
        <h2 className="sr-only">Rapport soumis avec succès</h2>
        <div style={{
          textAlign: "center", padding: "3rem 2rem",
          border: "0.5px solid var(--color-border-tertiary)",
          borderRadius: "var(--border-radius-lg)",
          background: "var(--color-background-primary)"
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: "50%",
            background: "var(--color-background-success)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 1.5rem"
          }}>
            <i className="ti ti-check" style={{ fontSize: 32, color: "var(--color-text-success)" }} />
          </div>
          <h2 style={{ margin: "0 0 8px", fontSize: 20, fontWeight: 500 }}>Rapport soumis avec succès</h2>
          <p style={{ color: "var(--color-text-secondary)", margin: "0 0 24px" }}>
            Le rapport de maintenance conditionnelle a été enregistré pour <strong>{form.machine && machineInfo?.label}</strong>
          </p>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, margin: "0 0 28px"
          }}>
            {[
              { label: "Contrôles OK", val: okCount, color: "#2d8a4e" },
              { label: "Contrôles NOK", val: nokCount, color: "#c0392b" },
              { label: "Total effectués", val: totalChecks, color: "#185fa5" },
            ].map(({ label, val, color }) => (
              <div key={label} style={{
                padding: "12px", background: "var(--color-background-secondary)",
                borderRadius: "var(--border-radius-md)"
              }}>
                <p style={{ margin: 0, fontSize: 22, fontWeight: 500, color }}>{val}</p>
                <p style={{ margin: 0, fontSize: 12, color: "var(--color-text-secondary)" }}>{label}</p>
              </div>
            ))}
          </div>
          <button
            onClick={() => { setSubmitted(false); setStep(0); setForm(f => ({ ...f, technicien: "", machine: "", machineSap: "", compteur: "", observations: "" })); setChecks(Object.fromEntries(Object.keys(checks).map(k => [k, null]))); }}
            style={{ ...inputStyle, width: "auto", padding: "10px 28px", cursor: "pointer", background: "#185fa5", color: "#fff", border: "none", fontWeight: 500 }}
          >
            Nouveau rapport
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "1.5rem 1rem", fontFamily: "var(--font-sans)" }}>
      <h2 className="sr-only">Rapport de maintenance préventive conditionnelle</h2>

      {/* Header */}
      <div style={{
        background: "var(--color-background-primary)",
        border: "0.5px solid var(--color-border-tertiary)",
        borderRadius: "var(--border-radius-lg)", padding: "1.25rem 1.5rem",
        marginBottom: 20, borderLeft: "3px solid #185fa5"
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
          <div>
            <p style={{ margin: 0, fontSize: 11, fontWeight: 500, color: "#185fa5", textTransform: "uppercase", letterSpacing: "0.08em" }}>SEBN TN — Service Maintenance</p>
            <h1 style={{ margin: "4px 0 2px", fontSize: 18, fontWeight: 500, color: "var(--color-text-primary)" }}>
              Rapport de maintenance préventive conditionnelle
            </h1>
            <p style={{ margin: 0, fontSize: 13, color: "var(--color-text-secondary)" }}>
              Surveillance basée sur l'état opérationnel
            </p>
          </div>
          <div style={{ textAlign: "right", flexShrink: 0 }}>
            <p style={{ margin: 0, fontSize: 11, color: "var(--color-text-secondary)" }}>Réf. PMC-AA-TN</p>
            <p style={{ margin: "2px 0 0", fontSize: 11, color: "var(--color-text-secondary)" }}>Maintenance conditionnelle</p>
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
                fontSize: 12, fontWeight: 500, cursor: i < step ? "pointer" : "default",
                background: i < step ? "#2d8a4e" : i === step ? "#185fa5" : "var(--color-background-secondary)",
                color: i <= step ? "#fff" : "var(--color-text-secondary)",
                border: i === step ? "none" : "0.5px solid var(--color-border-secondary)"
              }}
            >
              {i < step ? <i className="ti ti-check" style={{ fontSize: 14 }} /> : i + 1}
            </div>
            <span style={{
              fontSize: 12, marginLeft: 6, color: i === step ? "var(--color-text-primary)" : "var(--color-text-secondary)",
              fontWeight: i === step ? 500 : 400, whiteSpace: "nowrap"
            }}>{s}</span>
            {i < steps.length - 1 && (
              <div style={{ flex: 1, height: 1, background: i < step ? "#2d8a4e" : "var(--color-border-tertiary)", margin: "0 8px" }} />
            )}
          </div>
        ))}
      </div>

      <div style={{
        background: "var(--color-background-primary)",
        border: "0.5px solid var(--color-border-tertiary)",
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
                <Field label="Type d'action">
                  <select style={inputStyle} value={form.actionType} onChange={e => setField("actionType", e.target.value)}>
                    <option value="reset">Réinitialisation compteur</option>
                    <option value="replace">Remplacement composants</option>
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
                <Field label="Compteur opérationnel actuel">
                  <input style={inputStyle} type="number" placeholder="Ex: 300000" value={form.compteur} onChange={e => setField("compteur", e.target.value)} />
                </Field>
              </div>
            </Section>

            {form.machine && (
              <div style={{
                padding: "12px 16px", borderRadius: "var(--border-radius-md)",
                background: "var(--color-background-info)", marginTop: 8,
                border: "0.5px solid var(--color-border-info)"
              }}>
                <p style={{ margin: 0, fontSize: 13, color: "var(--color-text-info)", lineHeight: 1.6 }}>
                  <i className="ti ti-info-circle" style={{ marginRight: 6, fontSize: 14 }} aria-hidden="true" />
                  <strong>Maintenance conditionnelle :</strong> Cette maintenance est déclenchée selon l'état de la machine et les compteurs opérationnels.
                  Actions : réinitialisation de compteur ou remplacement de composants usagés.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ── STEP 1: Vérification & Inspection ── */}
        {step === 1 && (
          <div>
            <Section title="Vérification initiale" icon="inspection" color="#185fa5">
              <CheckRow
                label="Vérification du compteur opérationnel"
                note="Confirmer la lecture du compteur et documenter l'état initial"
                value={checks.compteur_verification}
                onChange={v => setCheck("compteur_verification", v)}
              />
              <CheckRow
                label="État initial de la machine"
                note="Inspection visuelle générale et fonctionnement machine"
                value={checks.etat_machine_initial}
                onChange={v => setCheck("etat_machine_initial", v)}
                withPhoto
              />
            </Section>

            <Section title="Inspection des composants" icon="list" color="#3B6D11">
              <div style={{
                padding: "10px 14px", borderRadius: "var(--border-radius-md)",
                background: "var(--color-background-secondary)", marginBottom: 12, fontSize: 13,
                color: "var(--color-text-secondary)", lineHeight: 1.6
              }}>
                <i className="ti ti-alert-triangle" style={{ color: "#BA7517", marginRight: 6 }} aria-hidden="true" />
                Inspecter les composants critiques pour déterminer leur état d'usure et prioriser les remplacements.
              </div>
              <CheckRow
                label="Inspection détaillée des composants critiques"
                note="Vérifier usure, corrosion, déformations, fuites"
                value={checks.inspection_composants}
                onChange={v => setCheck("inspection_composants", v)}
                withPhoto
              />
              <CheckRow
                label="Nettoyage et vérification générale"
                note="Nettoyer les zones d'usure et vérifier l'alignement"
                value={checks.nettoyage_verification}
                onChange={v => setCheck("nettoyage_verification", v)}
              />
            </Section>

            <Section title="Test fonctionnel" icon="cpu" color="#534AB7">
              <CheckRow
                label="Test de fonctionnement complet"
                note="Tester tous les cycles et vérifier le bon fonctionnement"
                value={checks.fonctionnement_teste}
                onChange={v => setCheck("fonctionnement_teste", v)}
              />
            </Section>
          </div>
        )}

        {/* ── STEP 2: Actions & Validation ── */}
        {step === 2 && (
          <div>
            <Section title="Actions effectuées" icon="tools" color="#185fa5">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
                <Field label="Type d'action">
                  <select style={inputStyle} value={form.actionType} onChange={e => setField("actionType", e.target.value)}>
                    <option value="reset">Réinitialisation compteur</option>
                    <option value="replace">Remplacement composants</option>
                  </select>
                </Field>
                {form.actionType === "replace" && (
                  <Field label="Composants remplacés">
                    <input style={inputStyle} placeholder="Ex: Lames de coupe, joints" value={form.componentsReplaced} onChange={e => setField("componentsReplaced", e.target.value)} />
                  </Field>
                )}
              </div>
            </Section>

            <Section title="Enregistrement et traçabilité" icon="folder" color="#3B6D11">
              <CheckRow
                label="Documentation complète"
                note="Photos enregistrées, compteur réinitialisé, composants documentés"
                value={checks.documentation_complete}
                onChange={v => setCheck("documentation_complete", v)}
              />
            </Section>

            <Section title="Observations et remarques" icon="note" color="#888780">
              <textarea
                style={{ ...inputStyle, minHeight: 90, resize: "vertical" }}
                placeholder="Détails de l'action effectuée, anomalies détectées, pièces remplacées, prochaines actions recommandées…"
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
                { label: "Progression", val: `${progress}%`, color: "#185fa5" },
                { label: "Contrôles OK", val: okCount, color: "#2d8a4e" },
                { label: "Contrôles NOK", val: nokCount, color: nokCount > 0 ? "#c0392b" : "var(--color-text-secondary)" },
                { label: "Non renseignés", val: allChecks - totalChecks, color: allChecks - totalChecks > 0 ? "#BA7517" : "var(--color-text-secondary)" },
              ].map(({ label, val, color }) => (
                <div key={label} style={{ padding: "12px 10px", background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", textAlign: "center" }}>
                  <p style={{ margin: 0, fontSize: 22, fontWeight: 500, color }}>{val}</p>
                  <p style={{ margin: 0, fontSize: 11, color: "var(--color-text-secondary)" }}>{label}</p>
                </div>
              ))}
            </div>

            <Section title="Récapitulatif de l'intervention" icon="list-check" color="#185fa5">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 13 }}>
                {[
                  ["Technicien", form.technicien || "—"],
                  ["Date", form.date],
                  ["Machine", machineInfo?.label || "—"],
                  ["SAP", form.machineSap || "—"],
                  ["Zone", form.machineArea || "—"],
                  ["Compteur", form.compteur ? `${Number(form.compteur).toLocaleString()}` : "—"],
                  ["Type d'action", ACTION_TYPES[form.actionType] || "—"],
                  ["Composants", form.componentsReplaced || "—"],
                ].map(([k, v]) => (
                  <div key={k} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "7px 10px", background: "var(--color-background-secondary)",
                    borderRadius: "var(--border-radius-md)"
                  }}>
                    <span style={{ color: "var(--color-text-secondary)" }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v}</span>
                  </div>
                ))}
              </div>
            </Section>

            {nokCount > 0 && (
              <div style={{
                padding: "12px 16px", borderRadius: "var(--border-radius-md)",
                background: "#FCEBEB", border: "0.5px solid #F09595", marginBottom: 16
              }}>
                <p style={{ margin: 0, fontSize: 13, color: "#501313", fontWeight: 500 }}>
                  <i className="ti ti-alert-circle" style={{ marginRight: 6 }} aria-hidden="true" />
                  {nokCount} contrôle{nokCount > 1 ? "s" : ""} NOK détecté{nokCount > 1 ? "s" : ""} — action corrective requise.
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
                background: "var(--color-background-info)", border: "0.5px solid var(--color-border-info)",
                fontSize: 13, color: "var(--color-text-info)"
              }}>
                <i className="ti ti-info-circle" style={{ marginRight: 6 }} aria-hidden="true" />
                La validation doit être assurée par un chef d'équipe maintenance après vérification que l'action est effectuée convenablement.
              </div>
            </Section>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
        <button
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0}
          style={{
            ...inputStyle, width: "auto", padding: "9px 20px", cursor: step === 0 ? "not-allowed" : "pointer",
            opacity: step === 0 ? 0.4 : 1, display: "flex", alignItems: "center", gap: 6
          }}
        >
          <i className="ti ti-arrow-left" style={{ fontSize: 14 }} aria-hidden="true" />
          Précédent
        </button>

        <span style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>
          Étape {step + 1} / {steps.length}
        </span>

        {step < steps.length - 1 ? (
          <button
            onClick={() => setStep(s => Math.min(steps.length - 1, s + 1))}
            style={{
              ...inputStyle, width: "auto", padding: "9px 20px", cursor: "pointer",
              background: "#185fa5", color: "#fff", border: "none", fontWeight: 500,
              display: "flex", alignItems: "center", gap: 6
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
              background: (!form.technicien || !form.machine) ? "var(--color-background-secondary)" : "#2d8a4e",
              color: (!form.technicien || !form.machine) ? "var(--color-text-secondary)" : "#fff",
              border: "none", fontWeight: 500, display: "flex", alignItems: "center", gap: 6,
              opacity: (!form.technicien || !form.machine) ? 0.6 : 1
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
