import React from 'react';
import { MessageSquare, Phone, Mail } from 'lucide-react';

export const LiveAgentFallback: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
      <div className="w-16 h-16 bg-chewy-blue rounded-full flex items-center justify-center">
        <MessageSquare className="w-8 h-8 text-white" />
      </div>
      
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900">
          Connect with a Live Agent
        </h3>
        <p className="text-gray-600 max-w-md">
          Our live chat agents are currently offline. Please use one of these options to get help:
        </p>
      </div>
      
      <div className="space-y-4 w-full max-w-sm">
        <a
          href="tel:1-800-672-4399"
          className="flex items-center justify-center space-x-3 bg-chewy-blue text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Phone className="w-5 h-5" />
          <span>Call 1-800-672-4399</span>
        </a>
        
        <a
          href="mailto:help@chewy.com"
          className="flex items-center justify-center space-x-3 border border-chewy-blue text-chewy-blue px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors"
        >
          <Mail className="w-5 h-5" />
          <span>Email help@chewy.com</span>
        </a>
      </div>
      
      <div className="text-sm text-gray-500">
        <p>Live chat hours: Monday-Friday, 6am-12am ET</p>
        <p>Saturday-Sunday, 8am-10pm ET</p>
      </div>
    </div>
  );
}; 