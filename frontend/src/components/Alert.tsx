interface AlertProps {
  type: 'success' | 'error' | 'info';
  message: string;
  onClose?: () => void;
}

export function Alert({ type, message, onClose }: AlertProps) {
  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  return (
    <div className={`border rounded-lg p-4 flex justify-between items-center ${colors[type]}`}>
      <span>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="text-xl font-bold hover:opacity-70"
        >
          ×
        </button>
      )}
    </div>
  );
}
