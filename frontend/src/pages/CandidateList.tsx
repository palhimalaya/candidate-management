import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { candidatesAPI } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Alert } from '../components/Alert';
import { Candidate, CandidateStatus } from '../types';
import { useDebounce } from '../hooks/useDebounce';

const PAGE_SIZE = 20;

export function CandidateList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);

  const page = Number(searchParams.get('page')) || 1;

  const debouncedStatus  = useDebounce(searchParams.get('status')       || '');
  const debouncedRole    = useDebounce(searchParams.get('role_applied')  || '');
  const debouncedSkill   = useDebounce(searchParams.get('skill')         || '');
  const debouncedKeyword = useDebounce(searchParams.get('keyword')       || '');

  useEffect(() => {
    let cancelled = false;

    const fetchCandidates = async () => {
      setLoading(true);
      setError('');

      try {
        const params: any = { page, page_size: PAGE_SIZE };

        if (debouncedStatus)  params.status       = debouncedStatus;
        if (debouncedRole)    params.role_applied  = debouncedRole;
        if (debouncedSkill)   params.skill         = debouncedSkill;
        if (debouncedKeyword) params.keyword       = debouncedKeyword;

        const response = await candidatesAPI.list(params);

        if (!cancelled) {
          setCandidates(response.data.data.items);
          setTotal(response.data.data.total);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to fetch candidates');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchCandidates();
    return () => { cancelled = true; };
  }, [page, debouncedStatus, debouncedRole, debouncedSkill, debouncedKeyword]);

  const handleFilterChange = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  const statusColors: Record<CandidateStatus, string> = {
    new:      'bg-blue-100 text-blue-800',
    reviewed: 'bg-yellow-100 text-yellow-800',
    hired:    'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Candidates</h1>

      {error && <Alert type="error" message={error} onClose={() => setError('')} />}

      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={searchParams.get('status') || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="">All</option>
              <option value="new">New</option>
              <option value="reviewed">Reviewed</option>
              <option value="hired">Hired</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <input
              type="text"
              placeholder="Software Engineer"
              value={searchParams.get('role_applied') || ''}
              onChange={(e) => handleFilterChange('role_applied', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Skill</label>
            <input
              type="text"
              placeholder="Python"
              value={searchParams.get('skill') || ''}
              onChange={(e) => handleFilterChange('skill', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Keyword</label>
            <input
              type="text"
              placeholder="Search name or email"
              value={searchParams.get('keyword') || ''}
              onChange={(e) => handleFilterChange('keyword', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <p className="text-gray-600">
            Showing {candidates.length} of {total} candidates
          </p>

          <div className="grid grid-cols-1 gap-4">
            {candidates.length === 0 ? (
              <div className="text-center py-12 text-gray-500">No candidates found</div>
            ) : (
              candidates.map((candidate) => (
                <Link
                  key={candidate.id}
                  to={`/candidates/${candidate.id}`}
                  className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow block"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{candidate.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${statusColors[candidate.status]}`}>
                      {candidate.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{candidate.email}</p>
                  <p className="font-medium text-gray-900 mb-3">{candidate.role_applied}</p>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.map((skill) => (
                      <span key={skill} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-md text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </Link>
              ))
            )}
          </div>

          <div className="flex justify-center items-center gap-4 py-4">
            <button
              onClick={() => handlePageChange(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
            >
              Previous
            </button>
            <span className="text-gray-600">
              Page {page} of {Math.max(1, Math.ceil(total / PAGE_SIZE))}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= Math.ceil(total / PAGE_SIZE)}
              className="px-4 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}