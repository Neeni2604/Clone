// This is for ChatMessages
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';


const ChatMessages = () => {
  const { chatId } = useParams();

  // Getting all the accounts to map account_id to usernames
  const { data: accountsData } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/accounts');
      // Create a mapping of account_id to username
      const accountMap = {};
      response.data.accounts.forEach(account => {
        accountMap[account.id] = account.username;
      });
      return accountMap;
    }
  });

  // Getting the messages for the selected chat
  const { data: messagesData, isLoading, error } = useQuery({
    queryKey: ['messages', chatId],
    queryFn: async () => {
      const response = await axios.get(`http://localhost:8000/chats/${chatId}/messages`);
      // Sorting all the messages by created_at date
      return response.data.messages.sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
      );
    },
    enabled: !!chatId, // if teh chatID is avaliable, run this. Else don't.
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getUsernameById = (accountId) => {
    if (!accountsData) return 'Loading...';
    return accountId ? accountsData[accountId] || 'Unknown User' : '[removed]';
  };

  return (
    <div className="flex-1 p-4 overflow-y-auto max-h-lvh bg-gray-50 space-y-4">
      {isLoading ? (
        <div className="text-center py-4">Loading messages...</div>
      ) : error ? (
        <div className="text-center py-4 text-red-600">Failed to fetch messages</div>
      ) : messagesData.length === 0 ? (
        <div className="text-center py-4 text-gray-500">No messages in this chat</div>
      ) : (
        <>
          {messagesData.map((message) => (
            <div key={message.id} className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex justify-between mb-2">
                <span className="font-medium">{getUsernameById(message.account_id)}</span>
                <span className="text-gray-500 text-sm">{formatDate(message.created_at)}</span>
              </div>
              <p className="text-gray-800">{message.text}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default ChatMessages;