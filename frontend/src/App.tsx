import { Routes, Route } from 'react-router-dom';
import SectorHub from './pages/SectorHub';
import SectorStatboard from './pages/SectorStatboard';
import CompanyDetail from './pages/CompanyDetail';
import Academy from './pages/Academy';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <Routes>
      <Route path="/"                    element={<SectorHub />} />
      <Route path="/sector/:sector_name" element={<SectorStatboard />} />
      <Route path="/company/:ticker"     element={<CompanyDetail />} />
      <Route path="/academy"             element={<Academy />} />
      <Route path="*"                    element={<NotFound />} />
    </Routes>
  );
}
