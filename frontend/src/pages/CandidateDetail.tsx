import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { candidatesAPI } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Alert } from '../components/Alert';
import { useAuth } from '../context/AuthContext';
import { CandidateWithScores, CandidateStatus } from '../types';

export function CandidateDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();

  const [candidate, setCandidate] = useState<CandidateWithScores | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [scoreForm, setScoreForm] = useState({ category: '', score: 3, note: '' });
  const [submittingScore, setSubmittingScore] = useState(false);

  const statusColors: Record<CandidateStatus, string> = {
    new: 'bg-blue-100 text-blue-800',
    reviewed: 'bg-yellow-100 text-yellow-800',
    hired: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };

  const fetchCandidate = async () => {
    if (!id) return;

    setLoading(true);
    setError('');

    try {
      const response = await candidatesAPI.getById(Number(id));
      setCandidate(response.data.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch candidate');
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async () => {
    if (!id) return;

    setSummaryLoading(true);
    setError('');

    try {
      const response = await candidatesAPI.generateSummary(Number(id));
      setCandidate((prev) =>
        prev ? { ...prev, ai_summary: response.data.data.ai_summary } : null
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate AI summary');
    } finally {
      setSummaryLoading(false);
    }
  };

  const submitScore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    setSubmittingScore(true);
    setError('');

    try {
      await candidatesAPI.createScore(Number(id), scoreForm);
      setScoreForm({ category: '', score: 3, note: '' });
      await fetchCandidate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit score');
    } finally {
      setSubmittingScore(false);
    }
  };

  useEffect(() => {
    fetchCandidate();
  }, [id]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!candidate) {
    return <div className="text-center py-12 text-gray-500">Candidate not found</div>;
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
      >
        ← Back
      </button>

      {error && <Alert type="error" message={error} onClose={() => setError('')} />}

      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {candidate.name}
            </h1>
            <div className="flex flex-wrap gap-3 items-center mb-2">
              <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${statusColors[candidate.status]}`}>
                {candidate.status}
              </span>
              <span className="text-gray-600">{candidate.email}</span>
              <span className="font-medium text-gray-900">{candidate.role_applied}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {candidate.skills.map((skill) => (
              <span
                key={skill}
                className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Scores</h2>
            {candidate.scores.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No scores yet</div>
            ) : (
              <div className="space-y-4">
                {candidate.scores.map((score) => (
                  <div
                    key={score.id}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {score.category}
                      </h3>
                      <span className="text-2xl font-bold text-indigo-600">
                        {score.score}/5
                      </span>
                    </div>
                    {score.note && (
                      <p className="text-gray-600 mb-2">{score.note}</p>
                    )}
                    <p className="text-sm text-gray-500">
                      by {score.reviewer_name} • {new Date(score.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add Score</h2>
            <form onSubmit={submitScore} className="space-y-4">
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <input
                  id="category"
                  type="text"
                  placeholder="e.g., Technical Skills, Communication"
                  value={scoreForm.category}
                  onChange={(e) => setScoreForm({ ...scoreForm, category: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="score" className="block text-sm font-medium text-gray-700 mb-1">
                  Score (1-5)
                </label>
                <input
                  id="score"
                  type="number"
                  min="1"
                  max="5"
                  value={scoreForm.score}
                  onChange={(e) =>
                    setScoreForm({ ...scoreForm, score: Number(e.target.value) })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="note" className="block text-sm font-medium text-gray-700 mb-1">
                  Note (optional)
                </label>
                <textarea
                  id="note"
                  rows={3}
                  placeholder="Add any additional notes..."
                  value={scoreForm.note}
                  onChange={(e) => setScoreForm({ ...scoreForm, note: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={submittingScore}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submittingScore ? 'Submitting...' : 'Submit Score'}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">AI Summary</h2>
              <button
                onClick={generateSummary}
                disabled={summaryLoading}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {summaryLoading ? 'Generating...' : 'Generate AI Summary'}
              </button>
            </div>
            {summaryLoading ? (
              <div className="flex flex-col items-center gap-4 py-8">
                <LoadingSpinner />
                <p className="text-gray-600">AI is analyzing candidate profile...</p>
              </div>
            ) : candidate.ai_summary ? (
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap text-gray-800 leading-relaxed">
                {candidate.ai_summary}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No AI summary yet. Click "Generate AI Summary" to create one.
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          {isAdmin && (
            <div className="bg-yellow-50 rounded-lg shadow-sm p-6 border border-yellow-200">
              <h2 className="text-xl font-bold text-yellow-800 mb-4">
                Admin Notes
              </h2>
              <div className="bg-white rounded-lg p-4 text-gray-900">
                {candidate.internal_notes || 'No admin notes'}
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-4">
              <div className="flex justify-between pb-4 border-b border-gray-200">
                <span className="font-medium text-gray-900">Created</span>
                <span className="text-gray-600">
                  {new Date(candidate.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
