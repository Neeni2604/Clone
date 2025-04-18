// importing ChatNavigation and ChatMessages
import ChatNavigation from '../components/ChatNavigation';
import ChatMessages from '../components/ChatMessages';

export function Home() {
  return (
    <div className="flex h-full">
      <div className="w-64">
        <ChatNavigation />
      </div>
      <div className="flex-1 flex items-center justify-center bg-gray-100">
        <div className="text-center p-8">
          <h2 className="text-2xl font-semibold text-gray-700">Welcome to Pony Express</h2>
          <p className="mt-2 text-gray-600">Select a chat from the sidebar to start messaging</p>
        </div>
      </div>
    </div>
  );
}

export function ChatPage() {
  return (
    <div className="flex h-full">
      <div className="w-64">
        <ChatNavigation />
      </div>
      <div className="flex-1">
        <ChatMessages />
      </div>
    </div>
  );
}

export function NotFound() {
  return (
    <div className="flex items-center justify-center h-full bg-gray-100">
      <div className="text-center p-8">
        <h1 className="text-4xl font-bold text-gray-800">404</h1>
        <p className="mt-2 text-xl text-gray-600">Page Not Found</p>
      </div>
    </div>
  );
}