import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { Activity, BarChart3, MapPin, Shield, Swords, Target, Users } from "lucide-react";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Batting from "./pages/Batting";
import { Bowling, Teams, HeadToHead, Venues, Players } from "./pages/AnalyticsPages";
const navigation = [["/","Dashboard",Activity],["/batting","Batting",Target],["/bowling","Bowling",BarChart3],["/teams","Teams",Shield],["/head-to-head","Head-to-Head",Swords],["/venues","Venues",MapPin],["/players","Players",Users]];
export function AppShell({children}) { return <div className="site-shell"><header className="topbar"><NavLink to="/" className="brand"><span className="brand-ball">◒</span><span>CRIC<span>IQ</span></span></NavLink><nav aria-label="Main navigation">{navigation.map(([to,label,Icon])=><NavLink end={to==="/"} to={to} key={to}><Icon size={15}/>{label}</NavLink>)}</nav><span className="data-status"><i/> Database analytics</span></header>{children}</div>; }
function Routed({children}) { return <AppShell>{children}</AppShell>; }
export default function App() { return <BrowserRouter><Routes><Route path="/" element={<Routed><Dashboard/></Routed>}/><Route path="/batting" element={<Routed><Batting/></Routed>}/><Route path="/bowling" element={<Routed><Bowling/></Routed>}/><Route path="/teams" element={<Routed><Teams/></Routed>}/><Route path="/head-to-head" element={<Routed><HeadToHead/></Routed>}/><Route path="/venues" element={<Routed><Venues/></Routed>}/><Route path="/players" element={<Routed><Players/></Routed>}/></Routes></BrowserRouter>; }
