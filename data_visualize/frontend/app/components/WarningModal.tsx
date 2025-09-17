import React from "react";

export default function WarningModal({ onAcknowledge }: { onAcknowledge: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-white p-10 rounded-none shadow-2xl max-w-2xl w-full mx-4 text-gray-800">
        <h1 className="text-3xl font-bold mb-6 text-red-600">⚠️ Content Warning</h1>
        <p className="text-lg leading-relaxed mb-4">
          The content you are about to access may include language, topics, or discussions that are
          considered adult, explicit, offensive, or inappropriate for some audiences. This includes:
        </p>
        <ul className="list-disc list-inside mb-4 text-base space-y-1">
          <li>Sexually explicit content</li>
          <li>Profanity or offensive language</li>
          <li>Descriptions of violence or harmful behavior</li>
          <li>Other sensitive or disturbing material</li>
        </ul>
        <p className="text-base mb-6">
          Viewer discretion is strongly advised. By continuing, you acknowledge that you are aware
          of these risks and are choosing to proceed.
        </p>
        <div className="flex justify-end">
          <button
            onClick={onAcknowledge}
            className="bg-red-600 hover:bg-red-700 text-white text-lg font-semibold px-6 py-3 rounded-none transition"
          >
            I Understand and Wish to Proceed
          </button>
        </div>
      </div>
    </div>
  );
}
