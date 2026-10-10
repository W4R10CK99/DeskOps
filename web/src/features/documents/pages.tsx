import { useMemo, useState } from 'react';
import { EmptyState, SearchInput } from '../../components/ui';
import { sampleDocuments } from '../projects/data';

export function DocumentsPage() {
  const [query, setQuery] = useState('');
  const [project, setProject] = useState('All projects');
  const filtered = useMemo(
    () =>
      sampleDocuments.filter(
        (document) =>
          `${document.name} ${document.project}`.toLowerCase().includes(query.toLowerCase()) &&
          (project === 'All projects' || document.project === project),
      ),
    [query, project],
  );
  const projects = [
    'All projects',
    ...new Set(sampleDocuments.map((document) => document.project)),
  ];
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">YOUR TEAM’S KNOWLEDGE</div>
          <h1>Documents</h1>
          <p>Keep the details close to the work they support.</p>
        </div>
        <button
          className="button button-secondary"
          disabled
          title="Upload becomes available after private storage is implemented"
        >
          ＋ Upload document
        </button>
      </div>
      <div className="document-callout">
        <span className="callout-icon">i</span>
        <div>
          <strong>Sample documents</strong>
          <p>
            These are demo entries only. Upload and download will be connected when private storage
            is implemented.
          </p>
        </div>
      </div>
      <section className="panel documents-panel">
        <div className="document-toolbar">
          <SearchInput value={query} onChange={setQuery} placeholder="Search documents…" />
          <select
            aria-label="Filter by project"
            className="filter-select"
            value={project}
            onChange={(event) => setProject(event.target.value)}
          >
            {projects.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <button
            className="filter-button"
            aria-label="Additional filters"
            title="Additional filters are not available in this demo"
            disabled
          >
            ☷
          </button>
        </div>
        {filtered.length ? (
          <div className="table-wrap">
            <table className="document-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Project</th>
                  <th>Updated</th>
                  <th>Size</th>
                  <th>
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((document) => (
                  <tr key={document.id}>
                    <td>
                      <div className="document-name">
                        <span className={`file-icon ${document.type.toLowerCase()}`}>
                          {document.type}
                        </span>
                        <span>
                          <strong>{document.name}</strong>
                          <small>{document.type} file</small>
                        </span>
                      </div>
                    </td>
                    <td>{document.project}</td>
                    <td>{document.updated}</td>
                    <td>{document.size}</td>
                    <td>
                      <button
                        className="icon-button"
                        aria-label={`More options for ${document.name}`}
                        title="File actions are not available in this demo"
                        disabled
                      >
                        ···
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No documents found">
            Try a different search or project filter.
          </EmptyState>
        )}
        <div className="table-footer">
          Showing {filtered.length} of {sampleDocuments.length} sample documents{' '}
          <span>● Demo workspace</span>
        </div>
      </section>
    </>
  );
}
