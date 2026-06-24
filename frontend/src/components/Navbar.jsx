import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/upload", label: "Upload Deals" },
  { to: "/chat", label: "AI Chat" },
];

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-logo">⚡</span>
        <span className="navbar-title">PipelineIQ</span>
      </div>
      <ul className="navbar-links">
        {links.map(({ to, label }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                "navbar-link" + (isActive ? " navbar-link--active" : "")
              }
            >
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}