import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function Header() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="text-2xl font-bold text-gray-900">
            TechKraft
          </Link>
          <nav className="flex gap-6">
            <Link
              to="/"
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Candidates
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <span className="text-gray-700 font-medium">{user?.name}</span>
            <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs font-semibold uppercase">
              {user?.role}
            </span>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
