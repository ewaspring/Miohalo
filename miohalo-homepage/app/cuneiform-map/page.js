import mapping from '../../data/az_cuneiform_selection';

const seedLetters = ['A', 'E', 'I', 'U', 'X'];

export default function CuneiformMapPage() {
  const rows = mapping;
  const selected = rows.filter((item) => item.status === 'selected');
  const seedSet = new Set(seedLetters);

  return (
    <main className="page">
      <section className="card">
        <p className="badge">MIOHALO · CUNEIFORM MAP</p>
        <h1>楔形文字 × 英文字母 A–Z 全量映射表</h1>
        <p>
          现在已通过分层匹配策略把 26 个字母全部匹配完成（26/26）。
          其中你之前先找到的 5 个核心字符 A/E/I/U/X 仍作为种子保留在结果中。
        </p>
        <div className="glyphList" aria-label="initial seed letters">
          {selected
            .filter((item) => seedSet.has(item.letter))
            .map((item) => (
              <div key={item.letter} className="glyphItem">
                <span className="glyphSymbol">{item.char}</span>
                <span>{item.letter}</span>
              </div>
            ))}
        </div>
      </section>

      <section className="card">
        <h2>完整 A–Z 对照</h2>
        <div className="tableWrap">
          <table className="mappingTable">
            <thead>
              <tr>
                <th>Letter</th>
                <th>Status</th>
                <th>Sign</th>
                <th>Codepoint</th>
                <th>Unicode Name</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((item) => (
                <tr key={item.letter}>
                  <td>{item.letter}</td>
                  <td>
                    <span className={`status ${item.status}`}>{item.status}</span>
                  </td>
                  <td className="glyphCell">{item.char || '-'}</td>
                  <td>{item.codepoint || '-'}</td>
                  <td>{item.name || '-'}</td>
                  <td>{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
