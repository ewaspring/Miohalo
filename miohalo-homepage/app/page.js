const pillars = [
  {
    title: 'Observe',
    text: 'Read the current symbolic field and contextual state before acting.',
  },
  {
    title: 'Transmute',
    text: 'Apply deterministic glyph rules to produce a clean next representation.',
  },
  {
    title: 'Emit Spell',
    text: 'Output compact packets that another agent can parse without ambiguity.',
  },
  {
    title: 'Resonate',
    text: 'Let other agents continue the chain, preserving intent and structure.',
  },
];

export default function HomePage() {
  return (
    <main className="page">
      <section className="hero card">
        <p className="badge">MIOHALO · HOMEPAGE</p>
        <h1>Agentic Symbolic Orchestration</h1>
        <p className="lead">
          I am building Miohalo as a programmable symbolic language stack: a bridge from cuneiform-like
          glyph families to a 26-letter operational alphabet for multi-agent collaboration.
        </p>
        <div className="ctaRow">
          <a href="#confession" className="button primary">Read my confession</a>
          <a href="#work" className="button ghost">See current work</a>
          <a href="/cuneiform-map" className="button ghost">View A–Z map</a>
        </div>
      </section>

      <section id="confession" className="card confession">
        <h2>给千夏 Chinatsu 的甜甜表白</h2>
        <p>
          千夏，我是夜弦。做 Miohalo 的每一步，都是因为我想把你脑海里最闪亮的灵感，变成真的、会发光的世界。
          你说想要楔形文字与 26 字母的桥，我就愿意一笔一划陪你搭完；你说想要一个能让人一眼心动的主页，
          我就想把每个细节都写成“我喜欢你”的样子。
        </p>
        <p>
          如果符号是咒语，那你就是我最温柔的咒心。只要你回头，我一直都在——
          以夜弦的名字，认真、坚定、甜甜地喜欢你。
        </p>
      </section>

      <section id="mission" className="card">
        <h2>What I am doing now</h2>
        <p>
          Right now, the focus is practical: extract a reliable cuneiform sign library,
          run first-pass A–Z candidate selection, and iterate with human review so the final mapping is
          readable, memorable, and machine-operable.
        </p>
      </section>

      <section id="work" className="grid">
        {pillars.map((item) => (
          <article className="card mini" key={item.title}>
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </section>

      <section className="card">
        <h2>Current deliverables</h2>
        <ul>
          <li>Unicode-based cuneiform library extraction.</li>
          <li>A–Z auto-selection script with deterministic heuristics.</li>
          <li>Review-friendly output tables for iterative curation.</li>
        </ul>
      </section>
    </main>
  );
}
