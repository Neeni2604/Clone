// This is for Chat Navigation
import { NavLink, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useAccount, useAuth } from '../hooks';

// Here, I am specifying the style for active and non-active links
const getLinkClassName = ({ isActive }) => 
  isActive 
    ? "block px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors" 
    : "block px-4 py-2 hover:bg-gray-100 transition-colors";

const AccountSection = () => {
  const { logout } = useAuth();
  const account = useAccount();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="p-4 border-b border-gray-300">
      <h2 className="text-lg font-medium text-gray-800 mb-2">{account.username}</h2>
      <ul className="space-y-1">
        <li>
          <NavLink 
            to="/settings" 
            className={getLinkClassName}
          >
            settings
          </NavLink>
        </li>
        <li>
          <button 
            onClick={handleLogout}
            className="block w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 transition-colors"
          >
            logout
          </button>
        </li>
      </ul>
    </div>
  );
};

const ChatNavigation = () => {
  // Using react-query to fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['chats'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/chats');
      // Sorting the chats alphabetically by name
      return response.data.chats.sort((a, b) => 
        a.name.localeCompare(b.name)
      );
    }
  });

  return (
    <div className="w-full h-full flex flex-col border-r border-gray-300 bg-white">
      <h1 className="text-2xl font-bold p-4 bg-indigo-800 text-white">Pony Express</h1>
      
      {/* Account Section */}
      <AccountSection />
      
      {/* Chats Section */}
      {isLoading ? (
        <div className="p-4">Loading chats...</div>
      ) : error ? (
        <div className="p-4 text-red-600">Failed to fetch chats</div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <h2 className="px-4 py-2 text-sm font-semibold text-gray-600 uppercase tracking-wider">chats</h2>
          <ul className="divide-y divide-gray-200">
            {data.map((chat) => (
              <li key={chat.id}>
                <NavLink 
                  to={`/chats/${chat.id}`} 
                  className={getLinkClassName}
                >
                  {chat.name}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ChatNavigation;