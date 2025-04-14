// This is for ChatNavigation
import { Link, Navigate, NavLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useAccount, useAuth } from '../hooks';

// Thisis teh style for the active chat
const getLinkClassName = ({ isActive }) => 
  isActive 
    ? "block px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors" 
    : "block px-4 py-2 bg-white hover:bg-gray-100 transition-colors";

const AccountNavigation = () => {
  const {logout} = useAuth();
  const account = useAccount();

  const handleLogout = () => {
    logout();
    return <Navigate to="/" />;
  }

  return (
    <ul>
      <h2>{account.username}</h2>
      <li>
        <NavLink to={"settings"} className={getLinkClassName}>
          Settings
        </NavLink>
      </li>
      <li>
        <Link onClick={handleLogout}>Logout</Link>
      </li>
    </ul>
  )
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
    <div className="w-full h-full flex flex-col border-r border-gray-300">
      <h1 className="text-2xl font-bold p-4 bg-indigo-800 text-white">Pony Express</h1>
      
      {isLoading ? (
        <div className="p-4">Loading chats...</div>
      ) : error ? (
        <div className="p-4 text-red-600">Failed to fetch chats</div>
      ) : (
        <nav className="flex-1 overflow-y-auto">
          <AccountNavigation />
          <ul className="divide-y divide-gray-300">
            <h2>chats</h2>
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
        </nav>
      )}
    </div>
  );
};

export default ChatNavigation;