import { useState } from 'react'
import api from './api';

function App() {
  const [responses, setResponses] = useState<string[]>([]);
  
  const handleClick = async () => {
    try {
      const response = await api.get("/hello");
      // Assuming the response is in the form { message: "hello world" }
      setResponses((prevResponses) => [...prevResponses, response.data.message]);
    } catch (error) {
      console.error("Error fetching the data", error);
    }
  };

  return (
    <div className="flex flex-col items-center p-4">
      <button 
        onClick={handleClick} 
        className="bg-blue-500 text-white py-2 px-4 rounded-lg mb-4"
      >
        Click Me
      </button>

      <div className="bg-gray-100 p-4 w-full max-w-md rounded-lg shadow-md overflow-y-auto h-60">
        <ul className="space-y-2">
          {responses.map((response, index) => (
            <li key={index} className="text-gray-800">{response}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App
