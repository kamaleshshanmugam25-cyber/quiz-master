# coding=utf-8
file_path = r"C:\A2757\QuizProject\frontend\src\pages\AudienceDisplay.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

qlb_start = text.find("function QuestionLeaderboard(")
det_start = text.find("function deterministicPosition(", qlb_start)

new_qlb = '''function QuestionLeaderboard({ leaderboard, profileRerenderTick, getUserProfileData }) {
  const [vis, setVis] = useState(false);
  useEffect(() => { const t = setTimeout(() => setVis(true), 250); return () => clearTimeout(t); }, []);
  if (!leaderboard.length) return null;
  const maxScore = leaderboard[0]?.score || 1;

  return (
    <div style={{ opacity: vis ? 1 : 0, transition: "opacity 0.4s ease" }}>
      <div style={{ background: "#ffffff", border: "2px solid #e2e8f0", borderRadius: 20, boxShadow: "0 10px 40px rgba(15, 23, 42, 0.05)", padding: "20px 22px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, paddingBottom: 10, borderBottom: "1.5px solid #f1f5f9" }}>
          <span style={{ fontSize: 11, letterSpacing: 2, textTransform: "uppercase", color: "#0f172a", fontFamily: "'DM Mono',monospace", fontWeight: 900 }}>
            CURRENT STANDINGS
          </span>
          <span style={{ fontSize: 12, color: "#64748b", fontFamily: "'DM Sans',sans-serif", fontWeight: 600 }}>
            {leaderboard.length} Ranked Players
          </span>
        </div>
        {leaderboard.length >= 1 && (
          <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
            {leaderboard.slice(0, Math.min(3, leaderboard.length)).map((p, i) => {
              const pd = getUserProfileData(p.username, p.avatar_id || 0, p.avatar_url || null);
              const sz = [52, 44, 40][i] || 40;
              const isFirst = i === 0;
              return (
                <div key={p.id || i} style={{
                  flex: isFirst ? 1.2 : 1,
                  background: isFirst ? "linear-gradient(135deg, #fffde6 0%, #fffc79 100%)" : "#f8fafc",
                  border: `2px solid ${isFirst ? "#fde047" : "#e2e8f0"}`,
                  borderRadius: 16,
                  padding: "14px 10px 12px",
                  textAlign: "center",
                  boxShadow: isFirst ? "0 4px 16px rgba(253, 224, 71, 0.35)" : "0 2px 8px rgba(15, 23, 42, 0.03)"
                }}>
                  <div style={{
                    display: "inline-block",
                    background: isFirst ? "#0f172a" : "#e2e8f0",
                    color: isFirst ? "#ffffff" : "#475569",
                    fontSize: 11,
                    fontFamily: "'DM Mono',monospace",
                    fontWeight: 900,
                    borderRadius: 99,
                    padding: "1px 9px",
                    marginBottom: 8
                  }}>
                    #{i + 1}
                  </div>
                  <div style={{ display: "flex", justifyContent: "center", marginBottom: 8 }}>
                    <div style={{ width: sz, height: sz, borderRadius: "50%", overflow: "hidden", border: `2px solid ${isFirst ? "#0f172a" : "#cbd5e1"}`, background: "#ffffff" }}>
                      <img src={pd.src} alt="" key={profileRerenderTick} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    </div>
                  </div>
                  <div style={{ color: "#0f172a", fontSize: 13, fontFamily: "'DM Sans',sans-serif", fontWeight: 800, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginBottom: 3 }}>
                    {p.username}
                  </div>
                  <div style={{ color: "#0f172a", fontSize: 16, fontFamily: "'DM Mono',monospace", fontWeight: 900, lineHeight: 1 }}>
                    {p.score.toLocaleString()}
                  </div>
                  <div style={{ color: "#64748b", fontSize: 9.5, fontFamily: "'DM Sans',sans-serif", marginTop: 2, fontWeight: 600 }}>pts</div>
                  <div style={{ marginTop: 8, height: 4, background: isFirst ? "rgba(15, 23, 42, 0.15)" : "#e2e8f0", borderRadius: 99, overflow: "hidden" }}>
                    <div style={{ height: "100%", background: "#0f172a", borderRadius: 99, width: `${maxScore > 0 ? (p.score / maxScore) * 100 : 0}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
        {leaderboard.length > 3 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {leaderboard.slice(3, 10).map((p, i) => {
              const pd = getUserProfileData(p.username, p.avatar_id || 0, p.avatar_url || null);
              return (
                <div key={p.id || i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 12 }}>
                  <div style={{ width: 24, fontFamily: "'DM Mono',monospace", fontSize: 11, fontWeight: 800, color: "#64748b", flexShrink: 0, textAlign: "center" }}>
                    #{i + 4}
                  </div>
                  <div style={{ width: 30, height: 30, borderRadius: "50%", overflow: "hidden", border: "1.5px solid #cbd5e1", flexShrink: 0, background: "#ffffff" }}>
                    <img src={pd.src} alt="" key={profileRerenderTick} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ color: "#0f172a", fontSize: 12, fontFamily: "'DM Sans',sans-serif", fontWeight: 700, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {p.username}
                    </div>
                  </div>
                  <div style={{ fontFamily: "'DM Mono',monospace", fontSize: 13, fontWeight: 800, color: "#0f172a", flexShrink: 0 }}>
                    {p.score.toLocaleString()} pts
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

'''

if qlb_start != -1 and det_start != -1:
    text = text[:qlb_start] + new_qlb + text[det_start:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("QuestionLeaderboard updated to white & playful!")
else:
    print("Could not find QuestionLeaderboard.")
