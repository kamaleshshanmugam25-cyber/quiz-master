import re

file_path = r"C:\A2757\QuizProject\frontend\src\pages\AudienceDisplay.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update QRPanel
qr_panel_target = '''function QRPanel({ sessionCode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, width: "100%" }}>
      <div style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: 10, borderBottom: "1px solid #f1f5f9" }}>
        <span style={{ fontSize: 9.5, letterSpacing: 2, textTransform: "uppercase", color: "#64748b", fontFamily: "'DM Mono',monospace", fontWeight: 700 }}>
          JOIN SESSION
        </span>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10, fontFamily: "'DM Mono',monospace", color: "#059669", fontWeight: 700 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#059669", boxShadow: "0 0 6px rgba(5,150,105,0.4)" }} />
          LIVE
        </span>
      </div>
      <div style={{
        background: "#ffffff",
        border: "1.5px solid #e2e8f0",
        borderRadius: 16,
        padding: 10,
        width: "100%",
        display: "flex",
        justifyContent: "center",
        boxSizing: "border-box",
        boxShadow: "0 2px 10px rgba(15, 23, 42, 0.04)"
      }}>
        <QRCode
          value={`${window.location.origin}/join/details?code=${sessionCode}`}
          size={144}
          qrStyle="squares"
          bgColor="#ffffff"
          fgColor="#0f172a"
          style={{ display: "block", width: "100%", height: "auto" }}
        />
      </div>

      {/* Crystal-Clear High-Contrast Session PIN Box */}
      <div style={{
        width: "100%",
        background: "#0f172a",
        border: "2px solid #0f172a",
        borderRadius: 16,
        padding: "14px 8px",
        textAlign: "center",
        boxSizing: "border-box",
        boxShadow: "0 4px 18px rgba(234, 88, 12, 0.25)"
      }}>
        <div style={{
          color: "#fffc79",
          fontFamily: "'DM Mono',monospace",
          fontSize: 10,
          letterSpacing: 2.5,
          textTransform: "uppercase",
          marginBottom: 5,
          fontWeight: 800
        }}>
          SESSION PIN
        </div>
        <div style={{
          color: "#ffffff",
          fontSize: 32,
          fontFamily: "'DM Mono',monospace",
          fontWeight: 800,
          letterSpacing: 6,
          lineHeight: 1,
          textShadow: "0 2px 10px rgba(0,0,0,0.5)"
        }}>
          {sessionCode}
        </div>
      </div>
    </div>
  );
}'''

qr_panel_replacement = '''function QRPanel({ sessionCode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, width: "100%" }}>
      {/* Game Station Header */}
      <div style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "4px 4px 10px",
        borderBottom: "1.5px dashed #f1f5f9"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 14 }}>🎮</span>
          <span style={{
            fontSize: 10,
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "#0f172a",
            fontFamily: "'DM Mono',monospace",
            fontWeight: 800
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
          color: "#059669",
          fontWeight: 800,
          background: "#ecfdf5",
          padding: "2px 7px",
          borderRadius: 99,
          border: "1px solid #a7f3d0"
        }}>
          <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 6px #10b981" }} />
          LIVE
        </span>
      </div>

      {/* Playful Game-Frame QR Code Card */}
      <div style={{
        background: "#ffffff",
        border: "2px solid #fde047",
        borderRadius: 20,
        padding: "12px 10px",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        boxSizing: "border-box",
        boxShadow: "0 4px 16px rgba(253, 224, 71, 0.3)",
        position: "relative"
      }}>
        <div style={{
          borderRadius: 12,
          overflow: "hidden",
          padding: 4,
          background: "#ffffff"
        }}>
          <QRCode
            value={`${window.location.origin}/join/details?code=${sessionCode}`}
            size={144}
            qrStyle="squares"
            bgColor="#ffffff"
            fgColor="#0f172a"
            style={{ display: "block", width: "100%", height: "auto" }}
          />
        </div>
        <span style={{
          marginTop: 8,
          fontSize: 10,
          fontFamily: "'DM Sans',sans-serif",
          fontWeight: 700,
          color: "#64748b",
          textAlign: "center",
          display: "flex",
          alignItems: "center",
          gap: 4
        }}>
          <span>📱</span> Scan to Play
        </span>
      </div>

      {/* Arcade Style GAME PIN Card */}
      <div style={{
        width: "100%",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        border: "2.5px solid #fffc79",
        borderRadius: 20,
        padding: "14px 8px",
        textAlign: "center",
        boxSizing: "border-box",
        boxShadow: "0 8px 24px -2px rgba(15, 23, 42, 0.25), 0 0 16px rgba(253, 224, 71, 0.25)",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{
          color: "#fffc79",
          fontFamily: "'DM Mono',monospace",
          fontSize: 10,
          letterSpacing: 2.5,
          textTransform: "uppercase",
          marginBottom: 5,
          fontWeight: 900,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 5
        }}>
          <span>⚡</span> GAME PIN
        </div>
        <div style={{
          color: "#ffffff",
          fontSize: 32,
          fontFamily: "'DM Mono',monospace",
          fontWeight: 900,
          letterSpacing: 5,
          lineHeight: 1,
          textShadow: "0 2px 10px rgba(0,0,0,0.6)"
        }}>
          {sessionCode}
        </div>
      </div>
    </div>
  );
}'''

if qr_panel_target in text:
    text = text.replace(qr_panel_target, qr_panel_replacement)
    print("1. Replaced QRPanel successfully.")
else:
    print("1. FAILED to find QRPanel target.")

# 2. Update VoteChoiceButtons
idx1 = text.find("function VoteChoiceButtons(")
idx2 = text.find("function VoteBarGraph(", idx1)

if idx1 != -1 and idx2 != -1:
    new_vote_buttons = '''function VoteChoiceButtons({ choices, shuffledChoices, onVote, votedChoiceId, counts }) {
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
              background: isVoted ? cfg.lightBg : "#ffffff",
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
                : "0 4px 16px rgba(15, 23, 42, 0.04)",
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
              width: 54, height: 54, borderRadius: 16, flexShrink: 0,
              background: cfg.badgeBg,
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              fontSize: 18, fontFamily: "'DM Mono',monospace", fontWeight: 900,
              color: cfg.badgeColor,
              boxShadow: `0 4px 12px ${cfg.glow}`,
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
                color: "#0f172a",
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
                  color: "#64748b",
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
    text = text[:idx1] + new_vote_buttons + text[idx2:]
    print("2. Replaced VoteChoiceButtons successfully.")
else:
    print("2. FAILED to locate VoteChoiceButtons boundaries.")

# 3. Update VoteBarGraph & AnswerRevealPanel
idx_bg = text.find("function VoteBarGraph(")
idx_ql = text.find("function QuestionLeaderboard(", idx_bg)

if idx_bg != -1 and idx_ql != -1:
    new_reveal_section = '''function VoteBarGraph({ choices, shuffledChoices, counts, phase }) {
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
    <div style={{ background: "#ffffff", border: "1.5px solid #e2e8f0", borderRadius: 20, padding: "20px 22px 18px", boxShadow: "0 4px 16px rgba(15, 23, 42, 0.04)" }}>
      {/* header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 13 }}>📊</span>
          <span style={{ fontSize: 10, letterSpacing: 2, textTransform: "uppercase", color: "#64748b", fontFamily: "'DM Mono',monospace", fontWeight: 800 }}>LIVE VOTES</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 18, fontFamily: "'DM Mono',monospace", fontWeight: 900, color: "#0f172a" }}>{totalVotes}</span>
          <span style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Sans',sans-serif", fontWeight: 600 }}>votes cast</span>
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
            ? (isCorrect ? "#10b981" : "#cbd5e1")
            : cfg.badgeBg;

          return (
            <div key={c.id} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, height: "100%", justifyContent: "flex-end" }}>
              {/* vote count */}
              <span style={{ fontSize: 13, fontFamily: "'DM Mono',monospace", fontWeight: 800, color: showCorrect ? (isCorrect ? "#059669" : "#94a3b8") : cfg.accent, opacity: v > 0 ? 1 : 0, transition: "opacity 0.3s" }}>
                {v}
              </span>
              {/* bar */}
              <div style={{ width: "52%", background: "#f8fafc", border: "1.5px solid #e2e8f0", borderRadius: "10px 10px 6px 6px", flex: 1, display: "flex", alignItems: "flex-end", overflow: "hidden" }}>
                <div style={{ width: "100%", height: `${h}%`, borderRadius: "8px 8px 0 0", background: barBg, transition: "height 0.9s cubic-bezier(0.22,1,0.36,1), background 0.5s ease" }} />
              </div>
              {/* letter badge */}
              <div style={{ width: 32, height: 32, borderRadius: 10, background: showCorrect ? (isCorrect ? "#10b981" : "#f1f5f9") : cfg.badgeBg, border: `1.5px solid ${showCorrect && isCorrect ? "#059669" : cfg.border}`, display: "flex", alignItems: "center", justifyContent: "center", color: showCorrect && isCorrect ? "#ffffff" : cfg.badgeColor, fontSize: 12, fontFamily: "'DM Mono',monospace", fontWeight: 800, transition: "all 0.4s ease" }}>
                {cfg.glyph} {cfg.label}
              </div>
              {/* correct tick */}
              <span style={{ fontSize: 10, fontFamily: "'DM Mono',monospace", letterSpacing: 1, color: "#059669", fontWeight: 900, visibility: showCorrect && isCorrect ? "visible" : "hidden" }}>✓</span>
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
          background: "#ffffff",
          border: "2px solid #fde047",
          borderRadius: 24,
          padding: "32px 42px",
          boxShadow: "0 10px 32px -4px rgba(15, 23, 42, 0.06), 0 0 20px rgba(253, 224, 71, 0.2)",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 12 }}>
          <span style={{
            fontSize: 11, letterSpacing: 2, textTransform: "uppercase",
            color: "#0f172a", fontFamily: "'DM Mono',monospace", fontWeight: 800,
            background: "linear-gradient(135deg, #fffde6 0%, #fffc79 100%)",
            border: "1.5px solid #fde047", borderRadius: 99, padding: "5px 18px",
            boxShadow: "0 2px 8px rgba(253, 224, 71, 0.3)"
          }}>
            🎉 ROUND RESULTS • ANSWER REVEALED
          </span>
        </div>
        <h2 style={{ color: "#0f172a", fontSize: "clamp(24px, 3.2vw, 36px)", margin: 0, fontFamily: "'DM Sans',sans-serif", fontWeight: 800, lineHeight: 1.35, letterSpacing: "-0.02em" }}>
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
                background: isCorrect ? "#ecfdf5" : "#ffffff",
                border: isCorrect ? "3px solid #10b981" : "1.5px solid #e2e8f0",
                borderBottom: isCorrect ? "5px solid #059669" : "4px solid #cbd5e1",
                boxShadow: isCorrect
                  ? "0 10px 32px -4px rgba(16, 185, 129, 0.3), 0 0 16px rgba(16, 185, 129, 0.15)"
                  : "0 2px 8px rgba(15, 23, 42, 0.02)",
                animation: `fadeUp 0.35s ${index * 0.05}s ease both`,
                opacity: isCorrect ? 1 : 0.5,
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
                background: isCorrect ? "#10b981" : "#cbd5e1",
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
                boxShadow: isCorrect ? "0 4px 14px rgba(16, 185, 129, 0.35)" : `0 2px 8px ${cfg.glow}`,
                lineHeight: 1.1
              }}>
                <span style={{ fontSize: 12, opacity: 0.9 }}>{cfg.glyph}</span>
                <span>{cfg.label}</span>
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  color: isCorrect ? "#064e3b" : "#475569",
                  fontSize: "clamp(18px, 2.3vw, 24px)",
                  fontFamily: "'DM Sans',sans-serif",
                  fontWeight: isCorrect ? 800 : 600,
                  lineHeight: 1.35
                }}>
                  {choice.text}
                </div>
                <div style={{ marginTop: 8, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                  {isCorrect ? (
                    <span style={{
                      color: "#047857",
                      fontSize: 11, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 1.2, textTransform: "uppercase",
                      display: "inline-flex", alignItems: "center", gap: 5,
                      background: "#d1fae5", padding: "3px 10px", borderRadius: 99, border: "1px solid #6ee7b7"
                    }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                      CORRECT ANSWER
                    </span>
                  ) : (
                    <span />
                  )}
                  <span style={{
                    color: isCorrect ? "#065f46" : "#64748b",
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
          background: "#ffffff",
          border: "2px solid #a7f3d0",
          borderRadius: 18,
          padding: "16px 26px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 6px 20px -2px rgba(16, 185, 129, 0.15)",
          animation: "fadeUp 0.4s ease both"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "#10b981",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#ffffff", flexShrink: 0,
              boxShadow: "0 4px 10px rgba(16, 185, 129, 0.4)"
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div>
              <span style={{ fontSize: 10.5, letterSpacing: 1.5, textTransform: "uppercase", color: "#047857", fontFamily: "'DM Mono',monospace", fontWeight: 800, marginRight: 8 }}>
                CORRECT ANSWER:
              </span>
              <span style={{ fontSize: 18, fontFamily: "'DM Sans',sans-serif", fontWeight: 800, color: "#0f172a" }}>
                {correctChoice.text}
              </span>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14, fontFamily: "'DM Mono',monospace", color: "#047857", fontWeight: 800 }}>
            <span>{correctCount} {correctCount === 1 ? "player" : "players"}</span>
            <span style={{ color: "#a7f3d0" }}>•</span>
            <span style={{ color: "#065f46", fontWeight: 700, fontSize: 13 }}>{total > 0 ? Math.round((correctCount / total) * 100) : 0}% answered correctly</span>
          </div>
        </div>
      )}
    </div>
  );
}

'''
    text = text[:idx_bg] + new_reveal_section + text[idx_ql:]
    print("3. Replaced VoteBarGraph and AnswerRevealPanel successfully.")
else:
    print("3. FAILED to locate VoteBarGraph and AnswerRevealPanel boundaries.")

# 4. Update Sidebar Players Badge
target_sidebar_players = '''        <div className="aud-sidebar-players" style={{
          background: "#ffffff",
          border: "1px solid #e2e8f0",
          borderRadius: 12,
          padding: "12px 14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          boxShadow: "0 1px 4px rgba(15, 23, 42, 0.02)"
        }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#059669", boxShadow: "0 0 6px rgba(5, 150, 105, 0.4)" }} />
          <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
            <span style={{ color: "#0f172a", fontSize: 18, fontFamily: "'DM Mono',monospace", fontWeight: 800 }}>{participants.length}</span>
            <span style={{ color: "#64748b", fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 600 }}>Connected</span>
          </div>
        </div>'''

new_sidebar_players = '''        <div className="aud-sidebar-players" style={{
          background: "linear-gradient(135deg, #fffde6 0%, #ffffff 100%)",
          border: "2px solid #fde047",
          borderRadius: 16,
          padding: "12px 14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          boxShadow: "0 3px 12px rgba(253, 224, 71, 0.25)"
        }}>
          <span style={{ fontSize: 18 }}>🕹️</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
            <span style={{ color: "#0f172a", fontSize: 20, fontFamily: "'DM Mono',monospace", fontWeight: 900 }}>{participants.length}</span>
            <span style={{ color: "#0f172a", fontFamily: "'DM Sans',sans-serif", fontSize: 12, fontWeight: 700 }}>
              {participants.length === 1 ? "Player Ready" : "Players Ready"}
            </span>
          </div>
        </div>'''

if target_sidebar_players in text:
    text = text.replace(target_sidebar_players, new_sidebar_players)
    print("4. Replaced Sidebar Players successfully.")
else:
    print("4. FAILED to find target_sidebar_players.")

# 5. Update Lobby Radar Arena and Question Keynote Stage
lobby_idx = text.find('{/* LOBBY: Playful Concentric Live Radar Arena */}')
question_end_idx = text.find('{/* CORRECT: Centered Keynote Stage */}')

if lobby_idx != -1 and question_end_idx != -1:
    new_lobby_and_question = '''{/* LOBBY: Simplified, Playful Live Radar Arena */}
        {phase === "lobby" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", justifyContent: "space-between" }}>
            {/* Header Stage */}
            <div style={{ textAlign: "center", marginBottom: 16, animation: "fadeUp 0.5s ease both", flexShrink: 0 }}>
              <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "linear-gradient(135deg, #fffde6 0%, #fffc79 100%)", border: "1.5px solid #fde047", borderRadius: 99, padding: "6px 20px", marginBottom: 8, boxShadow: "0 2px 10px rgba(253, 224, 71, 0.35)" }}>
                <span style={{ fontSize: 14 }}>🎮</span>
                <span style={{ fontSize: 10.5, letterSpacing: 2, textTransform: "uppercase", color: "#0f172a", fontFamily: "'DM Mono',monospace", fontWeight: 900 }}>GAME LOBBY</span>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </div>
              <h1 style={{ fontSize: "clamp(26px,3.8vw,42px)", margin: "0 0 6px", fontFamily: "'DM Sans',sans-serif", fontWeight: 900, letterSpacing: "-0.02em", color: "#0f172a" }}>
                Waiting for Players
              </h1>
              <p style={{ color: "#64748b", fontFamily: "'DM Sans',sans-serif", fontSize: 14, margin: 0, letterSpacing: 0.2 }}>
                Scan the QR code or enter Game PIN <strong style={{ color: "#0f172a", background: "#fffc79", padding: "3px 10px", borderRadius: 8, border: "1.5px solid #fde047", fontFamily: "'DM Mono',monospace", fontWeight: 900, boxShadow: "0 2px 6px rgba(253,224,71,0.4)" }}>{sessionCode}</strong> on your phone to join
              </p>
            </div>

            {/* Playful Radar Arena Stage */}
            <div
              style={{
                flex: 1,
                position: "relative",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                overflow: "hidden",
                minHeight: 440,
                width: "100%",
                background: "radial-gradient(circle at center, rgba(255, 252, 121, 0.22) 0%, rgba(254, 240, 138, 0.06) 48%, rgba(255, 255, 255, 0) 74%)",
                borderRadius: 28,
              }}
            >
              {/* Concentric clean game rings */}
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
                      border: `${isOuter ? "2px dashed" : "2px solid"} rgba(253, 224, 71, ${0.55 - i * 0.08})`,
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
                    border: "2px solid rgba(253, 224, 71, 0.8)",
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
                  background: "conic-gradient(from 0deg, rgba(253, 224, 71, 0.36) 0deg, rgba(253, 224, 71, 0.12) 28deg, rgba(253, 224, 71, 0.02) 50deg, transparent 65deg)",
                  zIndex: 3,
                }}
              >
                {/* Glowing leading sweep needle */}
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: "50%",
                    width: 2.5,
                    height: "50%",
                    transform: "translateX(-50%)",
                    background: "linear-gradient(180deg, #fde047 0%, rgba(253, 224, 71, 0.2) 100%)",
                    boxShadow: "0 0 10px #fde047, 0 0 4px #ffffff",
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
                    width: 76,
                    height: 76,
                    borderRadius: "50%",
                    border: "1.5px dashed #fde047",
                    animation: "ringSpinClockwise 12s linear infinite",
                    pointerEvents: "none",
                  }}
                />
                {/* Pulsing beacon glow */}
                <div
                  style={{
                    position: "absolute",
                    width: 62,
                    height: 62,
                    borderRadius: "50%",
                    background: "rgba(253, 224, 71, 0.28)",
                    animation: "beaconCorePulse 2.2s ease-in-out infinite",
                    pointerEvents: "none",
                  }}
                />
                {/* Core button/beacon */}
                <div
                  style={{
                    width: 52,
                    height: 52,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #fffc79 0%, #fde047 100%)",
                    border: "2.5px solid #ffffff",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 0 20px rgba(253, 224, 71, 0.8), 0 4px 14px rgba(15, 23, 42, 0.12)",
                    position: "relative",
                    zIndex: 2,
                  }}
                >
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#059669", boxShadow: "0 0 8px rgba(5,150,105,0.8)", marginBottom: 2 }} />
                  <span style={{ color: "#0f172a", fontSize: 8.5, fontFamily: "'DM Mono',monospace", fontWeight: 900, letterSpacing: 1.5 }}>LIVE</span>
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
                          gap: 4,
                          position: "relative",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: 3,
                            animation: `lobbyAvatarIn 0.55s ${entryDelay}s cubic-bezier(0.34,1.56,0.64,1) both`,
                            position: "relative",
                          }}
                        >
                          {/* Pulsing target blip ring underneath avatar */}
                          <div
                            style={{
                              position: "absolute",
                              width: 68,
                              height: 68,
                              borderRadius: "50%",
                              border: "2px solid rgba(253, 224, 71, 0.8)",
                              top: 29,
                              left: "50%",
                              transform: "translate(-50%, -50%)",
                              animation: "avatarBlipWave 2.8s ease-out infinite",
                              pointerEvents: "none",
                            }}
                          />

                          {/* Avatar Circle */}
                          <div
                            style={{
                              width: 58,
                              height: 58,
                              borderRadius: "50%",
                              padding: hasAttended ? 2 : 0,
                              background: hasAttended
                                ? `conic-gradient(#10b981 ${accuracy}%, rgba(253,224,71,0.4) ${accuracy}%)`
                                : "transparent",
                              border: hasAttended ? "none" : "3px solid #fffc79",
                              boxShadow: "0 6px 18px rgba(15,23,42,0.12), 0 0 0 2px #fde047",
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
                                background: "#ffffff",
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
                              color: "#0f172a",
                              fontSize: 11,
                              fontFamily: "'DM Sans',sans-serif",
                              fontWeight: 800,
                              maxWidth: 96,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                              textAlign: "center",
                              background: "#ffffff",
                              borderRadius: 8,
                              padding: "2.5px 10px",
                              border: "1.5px solid #fde047",
                              boxShadow: "0 2px 8px rgba(15,23,42,0.08)",
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
                              gap: 4,
                              fontSize: 9,
                              fontFamily: "'DM Mono', monospace, sans-serif",
                              fontWeight: 800,
                              color: hasAttended ? "#065f46" : "#713f12",
                              background: hasAttended ? "rgba(16,185,129,0.14)" : "#fffde6",
                              border: `1.5px solid ${hasAttended ? "rgba(16,185,129,0.4)" : "#fde047"}`,
                              borderRadius: 99,
                              padding: "2px 8px",
                              boxShadow: "0 1px 6px rgba(15,23,42,0.05)",
                              whiteSpace: "nowrap",
                              letterSpacing: 0.3,
                              position: "relative",
                              zIndex: 3,
                            }}
                          >
                            <span style={{ width: 5, height: 5, borderRadius: "50%", background: hasAttended ? "#10b981" : "#16a34a", boxShadow: "0 0 5px rgba(22,163,74,0.6)" }} />
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

              {/* Empty state when 0 participants */}
              {participants.length === 0 && (
                <div
                  style={{
                    position: "absolute",
                    top: "calc(50% + 56px)",
                    left: "50%",
                    transform: "translateX(-50%)",
                    zIndex: 12,
                    textAlign: "center",
                    background: "#ffffff",
                    border: "2px solid #fde047",
                    borderRadius: 16,
                    padding: "12px 28px",
                    boxShadow: "0 6px 20px rgba(253, 224, 71, 0.3)",
                    animation: "fadeUp 0.5s ease both",
                    whiteSpace: "nowrap",
                  }}
                >
                  <span style={{ fontSize: 13, color: "#0f172a", fontFamily: "'DM Sans',sans-serif", fontWeight: 700 }}>
                    🎮 Waiting for first player • Scan QR code to jump in!
                  </span>
                </div>
              )}

              {/* Pagination dots if > 28 players */}
              {participants.length > 28 && (
                <div style={{ position: "absolute", bottom: 8, left: "50%", transform: "translateX(-50%)", display: "flex", gap: 5, zIndex: 20 }}>
                  {Array.from({ length: Math.ceil(participants.length / 28) }).map((_, i) => (
                    <div key={i} style={{ width: i === lobbyPage ? 16 : 5, height: 5, borderRadius: 99, background: i === lobbyPage ? "#0f172a" : "#fde047", transition: "all 0.3s ease" }} />
                  ))}
                </div>
              )}
            </div>

            {/* Viewer Live Ticker Stage */}
            <div style={{ textAlign: "center", marginTop: 14, animation: "fadeUp 0.6s ease both", flexShrink: 0 }}>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  background: "#ffffff",
                  border: "1.5px solid #fde047",
                  borderRadius: 99,
                  padding: "6px 20px",
                  boxShadow: "0 2px 12px rgba(253, 224, 71, 0.25)",
                }}
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                </span>
                <span style={{ fontSize: 11, color: "#0f172a", fontFamily: "'DM Sans',sans-serif", fontWeight: 700 }}>
                  {participants.length === 0
                    ? "🎮 Grab your phone and scan the QR code to join the game!"
                    : participants.length === 1
                    ? `🎮 ${participants[0]?.username || "1 player"} is ready in the game! Waiting for more challengers...`
                    : `🎮 ${participants.length} challengers ready in the game! Presenter will start the quiz soon...`}
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
                background: "linear-gradient(135deg, #fffde6 0%, #fffc79 100%)",
                border: "1.5px solid #fde047",
                borderRadius: 99,
                padding: "7px 18px",
                boxShadow: "0 2px 8px rgba(253, 224, 71, 0.3)"
              }}>
                <span style={{ fontSize: 13 }}>🎯</span>
                <span style={{ color: "#0f172a", fontSize: 11, fontFamily: "'DM Mono',monospace", fontWeight: 800, letterSpacing: 2 }}>
                  LIVE QUESTION
                </span>
              </div>

              {/* Integrated Countdown Clock */}
              <div style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 12,
                background: isUrgent ? "#fff1f2" : "#ffffff",
                border: `2px solid ${isUrgent ? "#f43f5e" : "#fde047"}`,
                borderRadius: 99,
                padding: "6px 20px",
                boxShadow: isUrgent ? "0 4px 14px rgba(244, 63, 94, 0.25)" : "0 2px 10px rgba(253, 224, 71, 0.25)",
                animation: isUrgent ? "timerPulse 0.8s ease infinite" : "none"
              }}>
                <span style={{ fontSize: 15 }}>⏱️</span>
                <span style={{ fontSize: 17, fontFamily: "'DM Mono',monospace", fontWeight: 900, color: isUrgent ? "#e11d48" : "#0f172a" }}>
                  {timeLeft}s
                </span>
                <div style={{ width: 80, height: 6, background: "#f1f5f9", borderRadius: 99, overflow: "hidden", border: "1px solid #e2e8f0" }}>
                  <div style={{ height: "100%", width: `${timerPct}%`, background: isUrgent ? "#e11d48" : "#facc15", borderRadius: 99, transition: "width 0.25s linear" }} />
                </div>
              </div>
            </div>

            {/* Question Hero Card */}
            <div
              style={{
                background: "#ffffff",
                borderRadius: 24,
                padding: "36px 42px",
                textAlign: "center",
                flexShrink: 0,
                border: "2px solid #fde047",
                boxShadow: "0 10px 32px -4px rgba(15, 23, 42, 0.06), 0 0 20px rgba(253, 224, 71, 0.15)",
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
                color: "#713f12",
                fontFamily: "'DM Mono',monospace",
                fontWeight: 800,
                background: "#fffde6",
                border: "1px solid #fde047",
                borderRadius: 99,
                padding: "4px 14px",
                marginBottom: 14
              }}>
                <span>🕹️</span> SELECT YOUR ANSWER
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
                    boxShadow: "0 4px 16px rgba(15, 23, 42, 0.08)",
                  }}
                />
              )}
              <h2
                style={{
                  color: "#0f172a",
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

        '''
    text = text[:lobby_idx] + new_lobby_and_question + text[question_end_idx:]
    print("5. Replaced Lobby and Question sections successfully.")
else:
    print("5. FAILED to locate Lobby and Question boundaries.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("All done!")
