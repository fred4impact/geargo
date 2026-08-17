import './StarRatingInput.css';

interface StarRatingInputProps {
  value: number;
  onChange: (value: number) => void;
}

const StarRatingInput = ({ value, onChange }: StarRatingInputProps) => {
  return (
    <div className="star-rating-input" role="radiogroup" aria-label="Rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className={`star-btn ${star <= value ? 'filled' : ''}`}
          onClick={() => onChange(star)}
          aria-label={`${star} star${star > 1 ? 's' : ''}`}
          aria-checked={star === value}
          role="radio"
        >
          ★
        </button>
      ))}
    </div>
  );
};

export default StarRatingInput;
