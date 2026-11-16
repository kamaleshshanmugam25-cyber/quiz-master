import re

file_path = r"C:\A2757\QuizProject\frontend\src\pages\AudienceDisplay.js"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update APP_BG, FINAL_BG, CHOICE_CONFIG
old_cfg_start = code.find('const APP_BG')
old_cfg_end = code.find('const GLOBAL_STYLES', old_cfg_start)

new_cfg = '''const APP_BG    = "#070b14";
const FINAL_BG  = "#070b14";
const GOLD      = "#ffd700";
const GOLD_LIGHT= "#ffe566";
const GOLD_DARK = "#b8860b";
const GOLD_GLOW = "rgba(255,215,0,0.35)";
const TEAL      = "#00d4b8";
const PURPLE    = "#a78bfa";
const PINK      = "#fb7185";

const CHOICE_CONFIG = [
  {
    bg: "rgba(239, 68, 68, 0.12)",
    border: "#ef4444",
    hoverBg: "rgba(239, 68, 68, 0.22)",
    accent: "#ef4444",
    label: "A",
    glyph: "\\u25B2",
    badgeBg: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
    badgeBorder: "#b91c1c",
    badgeColor: "#ffffff",
    glow: "rgba(239, 68, 68, 0.35)",
    barBg: "#ef4444",
    lightBg: "rgba(239, 68, 68, 0.20)",
  },
  {
    bg: "rgba(59, 130, 246, 0.12)",
    border: "#3b82f6",
    hoverBg: "rgba(59, 130, 246, 0.22)",
    accent: "#2563eb",
    label: "B",
    glyph: "\\u25C6",
    badgeBg: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    badgeBorder: "#1d4ed8",
    badgeColor: "#ffffff",
    glow: "rgba(59, 130, 246, 0.35)",
    barBg: "#3b82f6",
    lightBg: "rgba(59, 130, 246, 0.20)",
  },
  {
    bg: "rgba(250, 204, 21, 0.12)",
    border: "#facc15",
    hoverBg: "rgba(250, 204, 21, 0.22)",
    accent: "#ca8a04",
    label: "C",
    glyph: "\\u25CF",
    badgeBg: "linear-gradient(135deg, #facc15 0%, #eab308 100%)",
    badgeBorder: "#a16207",
    badgeColor: "#713f12",
    glow: "rgba(250, 204, 21, 0.35)",
    barBg: "#eab308",
    lightBg: "rgba(250, 204, 21, 0.20)",
  },
  {
    bg: "rgba(16, 185, 129, 0.12)",
    border: "#10b981",
    hoverBg: "rgba(16, 185, 129, 0.22)",
    accent: "#059669",
    label: "D",
    glyph: "\\u25A0",
    badgeBg: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
    badgeBorder: "#047857",
    badgeColor: "#ffffff",
    glow: "rgba(16, 185, 129, 0.35)",
    barBg: "#10b981",
    lightBg: "rgba(16, 185, 129, 0.20)",
  },
];

'''

if old_cfg_start != -1 and old_cfg_end != -1:
    code = code[:old_cfg_start] + new_cfg + code[old_cfg_end:]
    print("1. Replaced APP_BG and CHOICE_CONFIG.")
else:
    print("1. FAILED to locate APP_BG.")

# 2. Update QRPanel
qr_idx = code.find("function QRPanel({ sessionCode }) {")
vote_btn_idx = code.find("function VoteChoiceButtons(", qr_idx)

new_qr_panel = '''function QRPanel({ sessionCode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, width: "100%" }}>
      {/* Game Station Header */}
      <div style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "4px 4px 10px",
        borderBottom: "1.5px solid rgba(255, 255, 255, 0.1)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 16 }}>\\uD83C\\uDFAE</span>
          <span style={{
            fontSize: 11,
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "#ffffff",
            fontFamily: "'DM Mono',monospace",
            fontWeight: 900
          }}>
            JOIN GAME
          </span>
        </div>
        <span style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 5,
          fontSize: 9.5,
          fontFamily: "'DM Mono',monospace",
          color: "#10b981",
          fontWeight: 800,
          background: "rgba(16, 185, 129, 0.15)",
          padding: "3px 8px",
          borderRadius: 99,
          border: "1px solid rgba(16, 185, 129, 0.4)"
        }}>
          <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 6px #10b981" }} />
          LIVE
        </span>
      </div>

      {/* Playful Game-Frame QR Code Card */}
      <div style={{
        background: "#ffffff",
        border: "2.5px solid #fffc79",
        borderRadius: 20,
        padding: "14px 12px",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        boxSizing: "border-box",
        boxShadow: "0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(255, 252, 121, 0.35)",
        position: "relative"
      }}>
        <div style={{
          borderRadius: 12,
          overflow: "hidden",
          padding: 2,
          background: "#ffffff"
        }}>
          <QRCode
            value={`${window.location.origin}/join/details?code=${sessionCode}`}
            size={168}
            qrStyle="squares"
            bgColor="#ffffff"
            fgColor="#0f172a"
            style={{ display: "block", width: "100%", height: "auto" }}
          />
        </div>
        <span style={{
          marginTop: 10,
          fontSize: 11,
          fontFamily: "'DM Sans',sans-serif",
          fontWeight: 800,
          color: "#0f172a",
          textAlign: "center",
          display: "flex",
          alignItems: "center",
          gap: 5
        }}>
          <span>\\uD83D\\uDCF1</span> Scan to Play
        </span>
      </div>

      {/* Arcade Style GAME PIN Card */}
      <div style={{
        width: "100%",
        background: "linear-gradient(135deg, #162035 0%, #0d1527 100%)",
        border: "2px solid #fffc79",
        borderRadius: 20,
        padding: "16px 10px",
        textAlign: "center",
        boxSizing: "border-box",
        boxShadow: "0 8px 24px rgba(0,0,0,0.4), 0 0 16px rgba(255, 252, 121, 0.25)",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{
          color: "#fffc79",
          fontFamily: "'DM Mono',monospace",
          fontSize: 11,
          letterSpacing: 3,
          textTransform: "uppercase",
          marginBottom: 6,
          fontWeight: 900,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6
        }}>
          <span>\\u26A1</span> GAME PIN
        </div>
        <div style={{
          color: "#ffffff",
          fontSize: 36,
          fontFamily: "'DM Mono',monospace",
          fontWeight: 900,
          letterSpacing: 6,
          lineHeight: 1,
          textShadow: "0 0 20px rgba(255, 252, 121, 0.4), 0 2px 10px rgba(0,0,0,0.8)"
        }}>
          {sessionCode}
        </div>
        <div style={{
          marginTop: 8,
          fontSize: 11,
          fontFamily: "'DM Sans',sans-serif",
          color: "rgba(255, 255, 255, 0.6)",
          fontWeight: 600
        }}>
          Enter at <strong style={{ color: "#fffc79" }}>{window.location.host}/join</strong>
        </div>
      </div>
    </div>
  );
}

'''

if qr_idx != -1 and vote_btn_idx != -1:
    code = code[:qr_idx] + new_qr_panel + code[vote_btn_idx:]
    print("2. Replaced QRPanel.")
else:
    print("2. FAILED to locate QRPanel.")

# 3. Update VoteChoiceButtons
vcb_idx = code.find("function VoteChoiceButtons(")
vbg_idx = code.find("function VoteBarGraph(", vcb_idx)

new_vcb = '''function VoteChoiceButtons({ choices, shuffledChoices, onVote, votedChoiceId, counts }) {
  const displayChoices = shuffledChoices.length ? shuffledChoices : choices;
  const totalVotes = Object.values(counts).reduce((a, b) => a + b, 0);
  const [animWidths, setAnimWidths] = useState({});

  useEffect(() => {
    const next = {};
    displayChoices.forEach(c => {
      next[c.id] = totalVotes > 0 ? Math.max(2, ((counts[c.id] || 0) / totalVotes) * 100) : 0;
    });
    const t = setTimeout(() => setAnimWidths(next), 120);
    return () => clearTimeout(t);
  }, [counts, totalVotes]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      {displayChoices.map((c, i) => {
        const cfg = CHOICE_CONFIG[i % 4];
        const isVoted = votedChoiceId === c.id;
        const isOther = votedChoiceId !== null && !isVoted;
        const voteCount = counts[c.id] || 0;
        const barW = animWidths[c.id] || 0;
        const pct = totalVotes > 0 ? Math.round((voteCount / totalVotes) * 100) : 0;

        return (
          <div
            key={c.id}
            onClick={() => onVote && onVote(c.id)}
            style={{
              position: "relative",
              overflow: "hidden",
              background: isVoted ? cfg.lightBg : "rgba(17, 26, 46, 0.85)",
              backdropFilter: "blur(12px)",
              border: isVoted ? `3px solid ${cfg.accent}` : `2px solid ${cfg.border}`,
              borderBottom: `5px solid ${cfg.accent}`,
              borderRadius: 20,
              padding: "22px 24px",
              transition: "all .2s cubic-bezier(0.34, 1.56, 0.64, 1)",
              display: "flex",
              alignItems: "center",
              gap: 18,
              textAlign: "left",
              opacity: isOther ? 0.6 : 1,
              transform: isVoted ? "scale(1.02) translateY(-2px)" : "scale(1)",
              boxShadow: isVoted
                ? `0 12px 28px -4px ${cfg.glow}`
                : "0 8px 24px rgba(0, 0, 0, 0.4)",
              cursor: onVote ? "pointer" : "default",
              minHeight: 104,
              boxSizing: "border-box",
            }}
          >
            {/* Poll animated progress fill */}
            <div style={{
              position: "absolute",
              left: 0, top: 0, bottom: 0,
              width: `${barW}%`,
              background: cfg.glow,
              borderRadius: "18px 0 0 18px",
              transition: "width 0.9s cubic-bezier(0.22,1,0.36,1)",
              pointerEvents: "none",
              opacity: totalVotes > 0 ? 1 : 0,
            }} />

            {/* Choice letter badge with glyph */}
            <div style={{
              width: 56, height: 56, borderRadius: 16, flexShrink: 0,
              background: cfg.badgeBg,
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              fontSize: 18, fontFamily: "'DM Mono',monospace", fontWeight: 900,
              color: cfg.badgeColor,
              boxShadow: `0 4px 14px ${cfg.glow}`,
              position: "relative",
              zIndex: 2,
              lineHeight: 1.1,
            }}>
              <span style={{ fontSize: 13, opacity: 0.95 }}>{cfg.glyph}</span>
              <span>{cfg.label}</span>
            </div>

            {/* Choice Text */}
            <div style={{
              flex: 1,
              position: "relative",
              zIndex: 2,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              gap: 6,
            }}>
              <span style={{
                fontSize: "clamp(18px, 2.3vw, 24px)",
                fontFamily: "'DM Sans', sans-serif",
                fontWeight: 800,
                color: "#ffffff",
                lineHeight: 1.35,
                wordBreak: "break-word",
              }}>
                {c.text}
              </span>
              {totalVotes > 0 && (
                <div style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 10,
                  fontSize: 13,
                  fontFamily: "'DM Mono',monospace",
                  color: "rgba(255, 255, 255, 0.65)",
                }}>
                  <span style={{ fontSize: 16, fontWeight: 900, color: cfg.accent }}>{pct}%</span>
                  <span style={{ fontWeight: 600 }}>({voteCount} {voteCount === 1 ? "vote" : "votes"})</span>
                </div>
              )}
            </div>

            {/* Checkmark when user voted for this */}
            {isVoted && (
              <div style={{
                position: "relative",
                zIndex: 2,
                width: 28,
                height: 28,
                borderRadius: "50%",
                background: cfg.accent,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                boxShadow: `0 2px 8px ${cfg.glow}`
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

'''

if vcb_idx != -1 and vbg_idx != -1:
    code = code[:vcb_idx] + new_vcb + code[vbg_idx:]
    print("3. Replaced VoteChoiceButtons.")
else:
    print("3. FAILED to locate VoteChoiceButtons.")

# 4. Update VoteBarGraph & AnswerRevealPanel
vbg_start = code.find("function VoteBarGraph(")
qlb_start = code.find("function QuestionLeaderboard(", vbg_start)

new_vbg_and_reveal = '''function VoteBarGraph({ choices, shuffledChoices, counts, phase }) {
  const displayChoices = shuffledChoices.length ? shuffledChoices : choices;
  const totalVotes = Object.values(counts).reduce((a, b) => a + b, 0);
  const showCorrect = phase === "correct" || phase === "answers_revealed";
  const [animHeights, setAnimHeights] = useState({});

  useEffect(() => {
    const next = {};
    displayChoices.forEach(c => { 
      next[c.id] = totalVotes > 0 ? Math.max(2, ((counts[c.id] || 0) / totalVotes) * 100) : 0;
    });
    const t = setTimeout(() => setAnimHeights(next), 120);
    return () => clearTimeout(t); 
  }, [counts, totalVotes]);

  return (
    <div style={{ background: "rgba(17, 26, 46, 0.85)", backdropFilter: "blur(14px)", border: "1.5px solid rgba(255, 252, 121, 0.2)", borderRadius: 20, padding: "20px 22px 18px", boxShadow: "0 8px 30px rgba(0, 0, 0, 0.4)" }}>
      {/* header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 13 }}>\\uD83D\\uDCCA</span>
          <span style={{ fontSize: 10, letterSpacing: 2, textTransform: "uppercase", color: "rgba(255, 255, 255, 0.7)", fontFamily: "'DM Mono',monospace", fontWeight: 800 }}>LIVE VOTES</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 18, fontFamily: "'DM Mono',monospace", fontWeight: 900, color: "#fffc79" }}>{totalVotes}</span>
          <span style={{ fontSize: 12, color: "rgba(255, 255, 255, 0.6)", fontFamily: "'DM Sans',sans-serif", fontWeight: 600 }}>votes cast</span>
        </div>
      </div>

      {/* 4 bars in one row */}
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${displayChoices.length}, 1fr)`, gap: 12, alignItems: "flex-end", height: 260 }}>
        {displayChoices.map((c, i) => {
          const cfg = CHOICE_CONFIG[i % 4];
          const v = counts[c.id] || 0;
          const h = animHeights[c.id] || 0;
          const isCorrect = c.is_correct;
          const barBg = showCorrect
            ? (isCorrect ? "#10b981" : "rgba(255, 255, 255, 0.2)")
            : cfg.badgeBg;

          return (
            <div key={c.id} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, height: "100%", justifyContent: "flex-end" }}>
              {/* vote count */}
              <span style={{ fontSize: 13, fontFamily: "'DM Mono',monospace", fontWeight: 800, color: showCorrect ? (isCorrect ? "#10b981" : "rgba(255,255,255,0.4)") : cfg.accent, opacity: v > 0 ? 1 : 0, transition: "opacity 0.3s" }}>
                {v}
              </span>
              {/* bar */}
              <div style={{ width: "52%", background: "rgba(255, 255, 255, 0.05)", border: "1.5px solid rgba(255, 255, 255, 0.1)", borderRadius: "10px 10px 6px 6px", flex: 1, display: "flex", alignItems: "flex-end", overflow: "hidden" }}>
                <div style={{ width: "100%", height: `${h}%`, borderRadius: "8px 8px 0 0", background: barBg, transition: "height 0.9s cubic-bezier(0.22,1,0.36,1), background 0.5s ease" }} />
              </div>
              {/* letter badge */}
              <div style={{ width: 32, height: 32, borderRadius: 10, background: showCorrect ? (isCorrect ? "#10b981" : "rgba(255,255,255,0.1)") : cfg.badgeBg, border: `1.5px solid ${showCorrect && isCorrect ? "#059669" : cfg.border}`, display: "flex", alignItems: "center", justifyContent: "center", color: showCorrect && isCorrect ? "#ffffff" : cfg.badgeColor, fontSize: 12, fontFamily: "'DM Mono',monospace", fontWeight: 800, transition: "all 0.4s ease" }}>
                {cfg.glyph} {cfg.label}
              </div>
              {/* correct tick */}
              <span style={{ fontSize: 10, fontFamily: "'DM Mono',monospace", letterSpacing: 1, color: "#10b981", fontWeight: 900, visibility: showCorrect && isCorrect ? "visible" : "hidden" }}>\\u2713</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AnswerRevealPanel({ currentQuestion, shuffledChoices, counts }) {
  if (!currentQuestion) return null;
  const total = Math.max(1, Object.values(counts).reduce((a, b) => a + b, 0));
  const displayChoices = shuffledChoices.length ? shuffledChoices : currentQuestion.choices;
  const correctChoice = displayChoices.find(c => c.is_correct);
  const correctCount = displayChoices.filter(c => c.is_correct).reduce((s, c) => s + (counts[c.id] || 0), 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 20, maxWidth: 1040, width: "100%", margin: "0 auto", padding: "10px 0" }}>
      {/* Question Hero Card */}
      <div
        style={{
          background: "linear-gradient(135deg, #111a2e 0%, #16223b 100%)",
          border: "2px solid #fffc79",
          borderRadius: 24,
          padding: "32px 42px",
          boxShadow: "0 20px 50px rgba(0,0,0,0.5), 0 0 25px rgba(255, 252, 121, 0.2)",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 12 }}>
          <span style={{
            fontSize: 11, letterSpacing: 2, textTransform: "uppercase",
            color: "#fffc79", fontFamily: "'DM Mono',monospace", fontWeight: 900,
            background: "rgba(255, 252, 121, 0.15)",
            border: "1.5px solid #fffc79", borderRadius: 99, padding: "5px 18px",
            boxShadow: "0 0 15px rgba(255, 252, 121, 0.3)"
          }}>
            \\uD83C\\uDF89 ROUND RESULTS \\u2022 ANSWER REVEALED
          </span>
        </div>
        <h2 style={{ color: "#ffffff", fontSize: "clamp(24px, 3.2vw, 36px)", margin: 0, fontFamily: "'DM Sans',sans-serif", fontWeight: 800, lineHeight: 1.35, letterSpacing: "-0.02em" }}>
          {currentQuestion.text}
        </h2>
      </div>

      {/* 4 Choices Grid (Game show style) */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2,minmax(0,1fr))", gap: 16 }}>
        {displayChoices.map((choice, index) => {
          const cfg = CHOICE_CONFIG[index % 4];
          const isCorrect = choice.is_correct;
          const voteCount = counts[choice.id] || 0;
          const pct = Math.round((voteCount / total) * 100);

          return (
            <div
              key={choice.id}
              style={{
                position: "relative",
                overflow: "hidden",
                borderRadius: 20,
                padding: "24px 28px",
                minHeight: 104,
                background: isCorrect ? "rgba(16, 185, 129, 0.22)" : "rgba(17, 26, 46, 0.75)",
                border: isCorrect ? "3px solid #10b981" : "1.5px solid rgba(255, 255, 255, 0.1)",
                borderBottom: isCorrect ? "5px solid #059669" : "4px solid rgba(255, 255, 255, 0.15)",
                boxShadow: isCorrect
                  ? "0 10px 32px rgba(16, 185, 129, 0.4), 0 0 20px rgba(16, 185, 129, 0.25)"
                  : "0 4px 16px rgba(0, 0, 0, 0.3)",
                animation: `fadeUp 0.35s ${index * 0.05}s ease both`,
                opacity: isCorrect ? 1 : 0.45,
                transform: isCorrect ? "scale(1.02)" : "scale(1)",
                display: "flex",
                alignItems: "center",
                gap: 20,
                boxSizing: "border-box"
              }}
            >
              {/* Animated Progress Fill */}
              <div style={{
                position: "absolute", left: 0, bottom: 0, height: 5, width: `${pct}%`,
                background: isCorrect ? "#10b981" : "rgba(255, 255, 255, 0.2)",
                transition: "width 0.8s ease"
              }} />

              {/* Letter badge with glyph */}
              <div style={{
                width: 52, height: 52, borderRadius: 16, flexShrink: 0,
                background: isCorrect ? "#10b981" : cfg.badgeBg,
                border: `1.5px solid ${isCorrect ? "#059669" : cfg.border}`,
                display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                color: isCorrect ? "#ffffff" : cfg.badgeColor,
                fontSize: 17, fontFamily: "'DM Mono',monospace", fontWeight: 900,
                boxShadow: isCorrect ? "0 4px 14px rgba(16, 185, 129, 0.4)" : `0 2px 8px ${cfg.glow}`,
                lineHeight: 1.1
              }}>
                <span style={{ fontSize: 12, opacity: 0.9 }}>{cfg.glyph}</span>
                <span>{cfg.label}</span>
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  color: isCorrect ? "#a7f3d0" : "#ffffff",
                  fontSize: "clamp(18px, 2.3vw, 24px)",
                  fontFamily: "'DM Sans',sans-serif",
                  fontWeight: isCorrect ? 900 : 600,
                  lineHeight: 1.35
                }}>
                  {choice.text}
                </div>
                <div style={{ marginTop: 8, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                  {isCorrect ? (
                    <span style={{
                      color: "#10b981",
                      fontSize: 11, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 1.2, textTransform: "uppercase",
                      display: "inline-flex", alignItems: "center", gap: 5,
                      background: "rgba(16, 185, 129, 0.2)", padding: "3px 10px", borderRadius: 99, border: "1px solid #10b981"
                    }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                      CORRECT ANSWER
                    </span>
                  ) : (
                    <span />
                  )}
                  <span style={{
                    color: isCorrect ? "#a7f3d0" : "rgba(255, 255, 255, 0.6)",
                    fontSize: 13, fontFamily: "'DM Mono',monospace", fontWeight: isCorrect ? 800 : 500
                  }}>
                    {pct}% ({voteCount} {voteCount === 1 ? "vote" : "votes"})
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Correct answer celebratory summary banner */}
      {correctChoice && (
        <div style={{
          background: "linear-gradient(135deg, #111a2e 0%, #16223b 100%)",
          border: "2px solid #10b981",
          borderRadius: 18,
          padding: "16px 26px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 10px 30px rgba(0,0,0,0.4), 0 0 20px rgba(16, 185, 129, 0.25)",
          animation: "fadeUp 0.4s ease both"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{
              width: 38, height: 38, borderRadius: "50%",
              background: "#10b981",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#ffffff", flexShrink: 0,
              boxShadow: "0 4px 12px rgba(16, 185, 129, 0.5)"
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div>
              <span style={{ fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase", color: "#34d399", fontFamily: "'DM Mono',monospace", fontWeight: 900, marginRight: 8 }}>
                CORRECT ANSWER:
              </span>
              <span style={{ fontSize: 18, fontFamily: "'DM Sans',sans-serif", fontWeight: 800, color: "#ffffff" }}>
                {correctChoice.text}
              </span>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14, fontFamily: "'DM Mono',monospace", color: "#34d399", fontWeight: 800 }}>
            <span>{correctCount} {correctCount === 1 ? "player" : "players"}</span>
            <span style={{ color: "rgba(255, 255, 255, 0.3)" }}>\\u2022</span>
            <span style={{ color: "rgba(255, 255, 255, 0.7)", fontWeight: 700, fontSize: 13 }}>{total > 0 ? Math.round((correctCount / total) * 100) : 0}% answered correctly</span>
          </div>
        </div>
      )}
    </div>
  );
}

'''

if vbg_start != -1 and qlb_start != -1:
    code = code[:vbg_start] + new_vbg_and_reveal + code[qlb_start:]
    print("4. Replaced VoteBarGraph and AnswerRevealPanel.")
else:
    print("4. FAILED to locate VoteBarGraph.")

# 5. Update main return and layout
ret_start = code.find("return (\n    <div className=\"aud-layout\"")
if ret_start == -1:
    ret_start = code.find("return (\r\n    <div className=\"aud-layout\"")

new_main_return = '''return (
    <div className="aud-layout" style={{ minHeight:"100vh", background: "radial-gradient(ellipse at 50% 10%, #172442 0%, #0d1527 50%, #070b14 100%)", fontFamily:"'DM Sans',sans-serif", position:"relative", overflow:"hidden", display:"flex", flexDirection:"column" }}>
      <style>{GLOBAL_STYLES}</style>
      <StarField count={70} />
      <FloatingOrbs count={14} />

      {/* Cinematic Marquee Top Bar */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "14px 28px",
        borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
        background: "rgba(7, 11, 20, 0.85)",
        backdropFilter: "blur(12px)",
        zIndex: 10,
        position: "relative",
        flexShrink: 0
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{
            background: "linear-gradient(135deg, #fffde6 0%, #fffc79 100%)",
            border: "1.5px solid #fde047",
            borderRadius: 12,
            padding: "5px 14px",
            fontSize: 12,
            fontFamily: "'DM Mono',monospace",
            fontWeight: 900,
            color: "#0f172a",
            letterSpacing: 1.5,
            boxShadow: "0 0 16px rgba(253, 224, 71, 0.45)"
          }}>
            \\uD83C\\uDFAE QUIZ ARENA
          </span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11, fontFamily: "'DM Mono',monospace", color: "#10b981", fontWeight: 800 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 8px #10b981" }} />
            LIVE AUDIENCE
          </span>
        </div>

        <div style={{
          fontSize: 13,
          fontFamily: "'DM Sans',sans-serif",
          fontWeight: 700,
          color: "rgba(255, 255, 255, 0.7)",
          display: "flex",
          alignItems: "center",
          gap: 6
        }}>
          <span>Join at:</span>
          <strong style={{ color: "#fffc79", background: "rgba(255, 252, 121, 0.12)", padding: "3px 12px", borderRadius: 8, border: "1px solid rgba(255, 252, 121, 0.35)", fontFamily: "'DM Mono',monospace", fontSize: 13 }}>
            {window.location.host}/join
          </strong>
        </div>

        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          background: "linear-gradient(135deg, #162035 0%, #0d1527 100%)",
          border: "2px solid #fffc79",
          borderRadius: 14,
          padding: "6px 18px",
          boxShadow: "0 0 20px rgba(255, 252, 121, 0.3)"
        }}>
          <span style={{ color: "#fffc79", fontSize: 11, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 1.5 }}>GAME PIN:</span>
          <span style={{ color: "#ffffff", fontSize: 22, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 4 }}>
            {sessionCode}
          </span>
        </div>
      </div>

      {/* Main Content Body */}
      <div style={{ flex: 1, display: "flex", flexDirection: "row", padding: "16px 24px", gap: 20, zIndex: 2, overflow: "hidden", minHeight: 0 }}>
        {/* Left Arcade Onboarding Station */}
        <div className="aud-sidebar" style={{
          width: 290,
          flexShrink: 0,
          background: "linear-gradient(180deg, #111a2e 0%, #0d1424 100%)",
          border: "2px solid rgba(255, 252, 121, 0.28)",
          borderRadius: 24,
          padding: "20px 16px",
          display: "flex",
          flexDirection: "column",
          gap: 16,
          boxShadow: "0 15px 40px rgba(0, 0, 0, 0.5), inset 0 0 30px rgba(255, 252, 121, 0.03)",
          boxSizing: "border-box"
        }}>
          <div className="aud-sidebar-qr"><QRPanel sessionCode={sessionCode} /></div>

          <div className="aud-sidebar-players" style={{
            background: "linear-gradient(135deg, #162035 0%, #0d1527 100%)",
            border: "2px solid rgba(255, 252, 121, 0.35)",
            borderRadius: 18,
            padding: "14px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 12,
            boxShadow: "0 4px 16px rgba(0,0,0,0.3)"
          }}>
            <span style={{ fontSize: 20 }}>\\uD83D\\uDD79\\uFE0F</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
              <span style={{ color: "#fffc79", fontSize: 24, fontFamily: "'DM Mono',monospace", fontWeight: 900, textShadow: "0 0 10px rgba(255,252,121,0.5)" }}>
                {participants.length}
              </span>
              <span style={{ color: "#ffffff", fontFamily: "'DM Sans',sans-serif", fontSize: 13, fontWeight: 800 }}>
                {participants.length === 1 ? "Player Ready" : "Players Ready"}
              </span>
            </div>
          </div>

          <div style={{ flex: 1 }} />
        </div>

        {/* Right Stage (Arena / Question / Reveal) */}
        <div className="aud-main" style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "8px 12px", zIndex: 2, overflowY: "auto", minWidth: 0 }}>
          {/* LOBBY: Spectacular, High-Contrast Live Radar Arena */}
          {phase === "lobby" && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", justifyContent: "space-between" }}>
              {/* Header Stage */}
              <div style={{ textAlign: "center", marginBottom: 12, animation: "fadeUp 0.5s ease both", flexShrink: 0 }}>
                <div style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  background: "linear-gradient(135deg, rgba(255, 252, 121, 0.2) 0%, rgba(255, 252, 121, 0.05) 100%)",
                  border: "1.5px solid #fffc79",
                  borderRadius: 99,
                  padding: "5px 18px",
                  marginBottom: 6,
                  boxShadow: "0 0 20px rgba(255, 252, 121, 0.3)"
                }}>
                  <span style={{ fontSize: 13 }}>\\uD83C\\uDFAE</span>
                  <span style={{ fontSize: 11, letterSpacing: 2, textTransform: "uppercase", color: "#fffc79", fontFamily: "'DM Mono',monospace", fontWeight: 900 }}>
                    LIVE RADAR ARENA
                  </span>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                </div>
                <h1 style={{ fontSize: "clamp(26px, 3.6vw, 42px)", margin: "0 0 4px", fontFamily: "'DM Sans',sans-serif", fontWeight: 900, letterSpacing: "-0.02em", color: "#ffffff" }}>
                  Waiting for Players
                </h1>
                <p style={{ color: "rgba(255, 255, 255, 0.65)", fontFamily: "'DM Sans',sans-serif", fontSize: 14, margin: 0, letterSpacing: 0.2 }}>
                  Scan the QR code or enter Game PIN <strong style={{ color: "#0f172a", background: "#fffc79", padding: "3px 12px", borderRadius: 8, border: "1.5px solid #fffc79", fontFamily: "'DM Mono',monospace", fontWeight: 900, boxShadow: "0 0 14px rgba(255,252,121,0.5)" }}>{sessionCode}</strong> to join
                </p>
              </div>

              {/* Playful Glowing Radar Stage */}
              <div
                style={{
                  flex: 1,
                  position: "relative",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  overflow: "hidden",
                  minHeight: 460,
                  width: "100%",
                  background: "radial-gradient(circle at center, #14223d 0%, #0d1629 55%, #080d19 100%)",
                  border: "2px solid rgba(255, 252, 121, 0.25)",
                  borderRadius: 28,
                  boxShadow: "0 25px 60px rgba(0,0,0,0.6), inset 0 0 60px rgba(14, 165, 233, 0.08)",
                }}
              >
                {/* Concentric clean, glowing game rings */}
                {[95, 175, 255, 335].map((r, i) => {
                  const isOuter = i === 3;
                  return (
                    <div
                      key={r}
                      style={{
                        position: "absolute",
                        width: r * 2,
                        height: r * 2,
                        borderRadius: "50%",
                        border: `${isOuter ? "2px dashed" : "2px solid"} rgba(255, 252, 121, ${0.45 - i * 0.08})`,
                        boxShadow: `0 0 16px rgba(255, 252, 121, ${0.15 - i * 0.02})`,
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%,-50%)",
                        pointerEvents: "none",
                        animation: isOuter ? "ringSpinClockwise 60s linear infinite" : "none",
                      }}
                    />
                  );
                })}

                {/* Sonar Expanding Waves */}
                {[160, 280].map((r, i) => (
                  <div
                    key={`pulse-${r}`}
                    style={{
                      position: "absolute",
                      width: r * 2,
                      height: r * 2,
                      borderRadius: "50%",
                      border: "2px solid rgba(255, 252, 121, 0.6)",
                      top: "50%",
                      left: "50%",
                      transform: "translate(-50%,-50%)",
                      animation: `radarPulseWave 4.5s ${i * 2.2}s cubic-bezier(0.1, 0.7, 0.3, 1) infinite`,
                      pointerEvents: "none",
                    }}
                  />
                ))}

                {/* THE ROTATING RADAR SWEEP BEAM */}
                <div
                  style={{
                    position: "absolute",
                    width: 580,
                    height: 580,
                    borderRadius: "50%",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%,-50%)",
                    pointerEvents: "none",
                    animation: "radarSweep 6.5s linear infinite",
                    background: "conic-gradient(from 0deg, rgba(255, 252, 121, 0.42) 0deg, rgba(255, 252, 121, 0.14) 28deg, rgba(255, 252, 121, 0.02) 50deg, transparent 65deg)",
                    zIndex: 3,
                  }}
                >
                  {/* Glowing leading sweep needle */}
                  <div
                    style={{
                      position: "absolute",
                      top: 0,
                      left: "50%",
                      width: 3,
                      height: "50%",
                      transform: "translateX(-50%)",
                      background: "linear-gradient(180deg, #ffffff 0%, #fffc79 40%, rgba(255, 252, 121, 0.1) 100%)",
                      boxShadow: "0 0 16px #fffc79, 0 0 4px #ffffff",
                    }}
                  />
                </div>

                {/* CENTER MULTI-TIER LIVE BEACON */}
                <div
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%,-50%)",
                    zIndex: 10,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {/* Outer spinning dashed ring */}
                  <div
                    style={{
                      position: "absolute",
                      width: 82,
                      height: 82,
                      borderRadius: "50%",
                      border: "2px dashed #fffc79",
                      animation: "ringSpinClockwise 12s linear infinite",
                      pointerEvents: "none",
                    }}
                  />
                  {/* Pulsing beacon glow */}
                  <div
                    style={{
                      position: "absolute",
                      width: 66,
                      height: 66,
                      borderRadius: "50%",
                      background: "rgba(255, 252, 121, 0.35)",
                      animation: "beaconCorePulse 2.2s ease-in-out infinite",
                      pointerEvents: "none",
                    }}
                  />
                  {/* Core button/beacon */}
                  <div
                    style={{
                      width: 56,
                      height: 56,
                      borderRadius: "50%",
                      background: "linear-gradient(135deg, #fffc79 0%, #facc15 100%)",
                      border: "3px solid #ffffff",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "0 0 25px rgba(255, 252, 121, 0.9), 0 4px 16px rgba(0,0,0,0.5)",
                      position: "relative",
                      zIndex: 2,
                    }}
                  >
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 10px #10b981", marginBottom: 2 }} />
                    <span style={{ color: "#0f172a", fontSize: 9, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 1.5 }}>LIVE</span>
                  </div>
                </div>

                {/* PLAYFUL FLOATING AVATARS */}
                {(() => {
                  const PAGE_SIZE = 28;
                  const paged = participants.slice(lobbyPage * PAGE_SIZE, (lobbyPage + 1) * PAGE_SIZE);
                  return paged.map((p, idx) => {
                    const globalIdx = lobbyPage * PAGE_SIZE + idx;
                    const safeName = String(p?.username || p?.name || `Player ${idx + 1}`);
                    const pos = deterministicPosition(safeName, sessionCode, globalIdx, participants.length);
                    const pd  = getUserProfileData(safeName, p.avatar_id, p.avatar_url || null);

                    let floatSeed = 0;
                    for (let i = 0; i < safeName.length; i++)
                      floatSeed = (floatSeed * 31 + safeName.charCodeAt(i)) >>> 0;
                    const floatDur   = (2.8 + (floatSeed % 1000) / 400).toFixed(2);
                    const floatDelay = (-((floatSeed % 3000) / 1000)).toFixed(2);
                    const entryDelay = (idx * 0.055).toFixed(2);

                    const totalAttended = Number(p.total_attended ?? 0);
                    const correctCount = Number(p.correct_count ?? 0);
                    const accuracy = totalAttended > 0 ? Math.round((correctCount / totalAttended) * 100) : 0;
                    const hasAttended = totalAttended > 0;

                    return (
                      <div
                        key={p.id || safeName || idx}
                        style={{
                          position: "absolute",
                          top: "50%",
                          left: "50%",
                          transform: `translate(calc(-50% + ${pos.x}px), calc(-50% + ${pos.y}px))`,
                          zIndex: 6,
                          pointerEvents: "none",
                        }}
                      >
                        <div
                          style={{
                            animation: `playfulAvatarFloat ${floatDur}s ${floatDelay}s ease-in-out infinite`,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: 5,
                            position: "relative",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              gap: 4,
                              animation: `lobbyAvatarIn 0.55s ${entryDelay}s cubic-bezier(0.34,1.56,0.64,1) both`,
                              position: "relative",
                            }}
                          >
                            {/* Pulsing target blip ring underneath avatar */}
                            <div
                              style={{
                                position: "absolute",
                                width: 72,
                                height: 72,
                                borderRadius: "50%",
                                border: "2px solid rgba(255, 252, 121, 0.8)",
                                top: 31,
                                left: "50%",
                                transform: "translate(-50%, -50%)",
                                animation: "avatarBlipWave 2.8s ease-out infinite",
                                pointerEvents: "none",
                              }}
                            />

                            {/* Avatar Circle */}
                            <div
                              style={{
                                width: 62,
                                height: 62,
                                borderRadius: "50%",
                                padding: 3,
                                background: hasAttended
                                  ? `conic-gradient(#10b981 ${accuracy}%, rgba(255,252,121,0.4) ${accuracy}%)`
                                  : "linear-gradient(135deg, #fffc79 0%, #facc15 100%)",
                                boxShadow: "0 8px 24px rgba(0,0,0,0.5), 0 0 16px rgba(255,252,121,0.5)",
                                overflow: "hidden",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexShrink: 0,
                                position: "relative",
                                zIndex: 2,
                              }}
                            >
                              <div
                                style={{
                                  width: "100%",
                                  height: "100%",
                                  borderRadius: "50%",
                                  overflow: "hidden",
                                  background: "#0f172a",
                                }}
                              >
                                <img
                                  src={pd.src}
                                  alt={safeName}
                                  key={profileRerenderTick}
                                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                                />
                              </div>
                            </div>

                            {/* Player Name */}
                            <div
                              style={{
                                color: "#ffffff",
                                fontSize: 12,
                                fontFamily: "'DM Sans',sans-serif",
                                fontWeight: 800,
                                maxWidth: 110,
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                textAlign: "center",
                                background: "rgba(15, 23, 42, 0.9)",
                                backdropFilter: "blur(8px)",
                                borderRadius: 8,
                                padding: "3px 12px",
                                border: "1.5px solid #fffc79",
                                boxShadow: "0 4px 14px rgba(0,0,0,0.4)",
                                position: "relative",
                                zIndex: 3,
                              }}
                            >
                              {safeName}
                            </div>

                            {/* Stat / Status Chip */}
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: 5,
                                fontSize: 9.5,
                                fontFamily: "'DM Mono', monospace, sans-serif",
                                fontWeight: 900,
                                color: hasAttended ? "#34d399" : "#fffc79",
                                background: hasAttended ? "rgba(16,185,129,0.2)" : "rgba(255,252,121,0.15)",
                                border: `1.5px solid ${hasAttended ? "#10b981" : "#fffc79"}`,
                                borderRadius: 99,
                                padding: "2px 9px",
                                boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
                                whiteSpace: "nowrap",
                                letterSpacing: 0.5,
                                position: "relative",
                                zIndex: 3,
                              }}
                            >
                              <span style={{ width: 6, height: 6, borderRadius: "50%", background: hasAttended ? "#10b981" : "#fffc79", boxShadow: `0 0 6px ${hasAttended ? "#10b981" : "#fffc79"}` }} />
                              {hasAttended ? (
                                <span>{correctCount}/{totalAttended} ({accuracy}%)</span>
                              ) : (
                                <span>READY</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  });
                })()}

                {/* Centered Clean Empty state when 0 participants */}
                {participants.length === 0 && (
                  <div
                    style={{
                      position: "absolute",
                      top: "calc(50% + 54px)",
                      left: "50%",
                      transform: "translateX(-50%)",
                      zIndex: 12,
                      textAlign: "center",
                      background: "rgba(15, 23, 42, 0.9)",
                      backdropFilter: "blur(12px)",
                      border: "2px solid #fffc79",
                      borderRadius: 16,
                      padding: "12px 28px",
                      boxShadow: "0 10px 30px rgba(0,0,0,0.6), 0 0 20px rgba(255, 252, 121, 0.25)",
                      animation: "fadeUp 0.5s ease both",
                      whiteSpace: "nowrap",
                    }}
                  >
                    <span style={{ fontSize: 13, color: "#fffc79", fontFamily: "'DM Mono',monospace", fontWeight: 800 }}>
                      \\uD83C\\uDFAE WAITING FOR PLAYERS \\u2022 SCAN QR TO ENTER THE ARENA!
                    </span>
                  </div>
                )}

                {/* Pagination dots if > 28 players */}
                {participants.length > 28 && (
                  <div style={{ position: "absolute", bottom: 12, left: "50%", transform: "translateX(-50%)", display: "flex", gap: 6, zIndex: 20 }}>
                    {Array.from({ length: Math.ceil(participants.length / 28) }).map((_, i) => (
                      <div key={i} style={{ width: i === lobbyPage ? 18 : 6, height: 6, borderRadius: 99, background: i === lobbyPage ? "#fffc79" : "rgba(255,252,121,0.3)", boxShadow: i === lobbyPage ? "0 0 8px #fffc79" : "none", transition: "all 0.3s ease" }} />
                    ))}
                  </div>
                )}
              </div>

              {/* Viewer Live Ticker Stage */}
              <div style={{ textAlign: "center", marginTop: 12, animation: "fadeUp 0.6s ease both", flexShrink: 0 }}>
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 10,
                    background: "rgba(15, 23, 42, 0.8)",
                    backdropFilter: "blur(8px)",
                    border: "1.5px solid rgba(255, 252, 121, 0.35)",
                    borderRadius: 99,
                    padding: "7px 24px",
                    boxShadow: "0 4px 18px rgba(0,0,0,0.3)",
                  }}
                >
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                  </span>
                  <span style={{ fontSize: 12, color: "#ffffff", fontFamily: "'DM Sans',sans-serif", fontWeight: 700 }}>
                    {participants.length === 0
                      ? "\\uD83C\\uDFAE Grab your phone and scan the QR code to join the game!"
                      : participants.length === 1
                      ? `\\uD83C\\uDFAE ${participants[0]?.username || "1 player"} is ready in the arena! Waiting for more challengers...`
                      : `\\uD83C\\uDFAE ${participants.length} challengers ready in the arena! Presenter will start the quiz soon...`}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* QUESTION: Centered Keynote Game Stage */}
          {phase === "question" && currentQuestion && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 20, animation: "fadeUp 0.4s ease both", maxWidth: 1040, width: "100%", margin: "0 auto", padding: "10px 0" }}>
              {/* Top Bar Header */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, flexShrink: 0, width: "100%" }}>
                <div style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  background: "linear-gradient(135deg, rgba(255, 252, 121, 0.2) 0%, rgba(255, 252, 121, 0.05) 100%)",
                  border: "1.5px solid #fffc79",
                  borderRadius: 99,
                  padding: "7px 18px",
                  boxShadow: "0 0 16px rgba(255, 252, 121, 0.3)"
                }}>
                  <span style={{ fontSize: 13 }}>\\uD83C\\uDFAF</span>
                  <span style={{ color: "#fffc79", fontSize: 11, fontFamily: "'DM Mono',monospace", fontWeight: 800, letterSpacing: 2 }}>
                    LIVE QUESTION
                  </span>
                </div>

                {/* Integrated Countdown Clock */}
                <div style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 12,
                  background: isUrgent ? "rgba(244, 63, 94, 0.2)" : "rgba(15, 23, 42, 0.8)",
                  border: `2px solid ${isUrgent ? "#f43f5e" : "#fffc79"}`,
                  borderRadius: 99,
                  padding: "6px 20px",
                  boxShadow: isUrgent ? "0 0 20px rgba(244, 63, 94, 0.4)" : "0 0 16px rgba(255, 252, 121, 0.25)",
                  animation: isUrgent ? "timerPulse 0.8s ease infinite" : "none"
                }}>
                  <span style={{ fontSize: 15 }}>\\u23F1\\uFE0F</span>
                  <span style={{ fontSize: 17, fontFamily: "'DM Mono',monospace", fontWeight: 900, color: isUrgent ? "#f43f5e" : "#fffc79" }}>
                    {timeLeft}s
                  </span>
                  <div style={{ width: 80, height: 6, background: "rgba(255, 255, 255, 0.1)", borderRadius: 99, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.1)" }}>
                    <div style={{ height: "100%", width: `${timerPct}%`, background: isUrgent ? "#f43f5e" : "#fffc79", borderRadius: 99, transition: "width 0.25s linear" }} />
                  </div>
                </div>
              </div>

              {/* Question Hero Card */}
              <div
                style={{
                  background: "linear-gradient(135deg, #111a2e 0%, #16223b 100%)",
                  borderRadius: 24,
                  padding: "36px 42px",
                  textAlign: "center",
                  flexShrink: 0,
                  border: "2px solid #fffc79",
                  boxShadow: "0 20px 50px rgba(0,0,0,0.5), 0 0 25px rgba(255, 252, 121, 0.2)",
                  position: "relative",
                  overflow: "hidden",
                  width: "100%",
                  boxSizing: "border-box"
                }}
              >
                <div style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 10.5,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  color: "#fffc79",
                  fontFamily: "'DM Mono',monospace",
                  fontWeight: 900,
                  background: "rgba(255, 252, 121, 0.15)",
                  border: "1px solid #fffc79",
                  borderRadius: 99,
                  padding: "4px 14px",
                  marginBottom: 14
                }}>
                  <span>\\uD83D\\uDD79\\uFE0F</span> SELECT YOUR ANSWER
                </div>
                {currentQuestion.image && (
                  <img
                    src={currentQuestion.image}
                    alt="Q"
                    style={{
                      maxWidth: "100%",
                      maxHeight: 180,
                      borderRadius: 14,
                      marginBottom: 20,
                      objectFit: "contain",
                      boxShadow: "0 4px 16px rgba(0, 0, 0, 0.4)",
                    }}
                  />
                )}
                <h2
                  style={{
                    color: "#ffffff",
                    fontSize: "clamp(24px, 3.4vw, 36px)",
                    lineHeight: 1.35,
                    margin: 0,
                    fontFamily: "'DM Sans', sans-serif",
                    fontWeight: 800,
                    letterSpacing: "-0.02em",
                  }}
                >
                  {currentQuestion.text}
                </h2>
              </div>

              {/* Substantial Choice Cards */}
              <VoteChoiceButtons choices={currentQuestion.choices} shuffledChoices={shuffledChoices} onVote={handleVote} votedChoiceId={votedChoiceId} counts={counts} />
            </div>
          )}

          {/* CORRECT: Centered Keynote Stage */}
          {phase === "correct" && currentQuestion && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", animation: "fadeUp 0.4s ease both", maxWidth: 1040, width: "100%", margin: "0 auto", padding: "10px 0" }}>
              <AnswerRevealPanel currentQuestion={currentQuestion} shuffledChoices={shuffledChoices} counts={counts} />
            </div>
          )}

          {/* FALLBACK */}
          {!["lobby","question","correct","final"].includes(phase) && (
            <div style={{ flex:1, animation:"fadeUp 0.4s ease both" }}>
              <div className="glass" style={{ padding:"32px", textAlign:"center", marginBottom:16 }}>
                <p style={{ color:"rgba(255, 255, 255, 0.7)", fontFamily:"'DM Sans',sans-serif", margin:0, fontSize:14, fontWeight:600 }}>Waiting for the next question...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <FlyingEmojiContainer emojis={emojiReactions} onEmojiComplete={()=>{}} />
    </div> 
  );
}
'''

if ret_start != -1:
    code = code[:ret_start] + new_main_return
    print("5. Replaced main return and layout.")
else:
    print("5. FAILED to locate main return.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Done writing cinematic audience!")
