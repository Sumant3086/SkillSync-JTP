import { useState } from 'react';

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label: string;
  hint?: string;
}

function MultiSelect({ options, selected, onChange, label, hint }: MultiSelectProps) {
  const [search, setSearch] = useState('');

  const filtered = search.trim()
    ? options.filter(o => o.toLowerCase().includes(search.toLowerCase()))
    : options;

  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter(item => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const removeTag = (option: string) => {
    onChange(selected.filter(item => item !== option));
  };

  return (
    <div className="form-group multi-select">
      <label className="form-label">{label}</label>
      {hint && <span className="form-hint">{hint}</span>}

      <div className="multiselect-search-wrap">
        <input
          type="text"
          className="multiselect-search"
          placeholder="Search options…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {search && (
          <button className="multiselect-search-clear" onClick={() => setSearch('')}>
            ×
          </button>
        )}
      </div>

      <div className="select-grid">
        {filtered.length === 0 ? (
          <span className="select-empty">No options match "{search}"</span>
        ) : (
          filtered.map(option => (
            <div
              key={option}
              className={`select-option ${selected.includes(option) ? 'selected' : ''}`}
              onClick={() => toggleOption(option)}
            >
              {option}
            </div>
          ))
        )}
      </div>

      {selected.length > 0 && (
        <div className="selected-tags">
          {selected.map(item => (
            <span key={item} className="tag">
              {item}
              <span className="tag-remove" onClick={() => removeTag(item)}>×</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default MultiSelect;
