import '@testing-library/jest-dom';
import { render, screen, act } from '@testing-library/react';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';

describe('ImageWithFallback', () => {
  it('renderiza la imagen cuando no hay error', () => {
    render(<ImageWithFallback src="/ok.png" alt="img" />);
    const img = screen.getByAltText('img') as HTMLImageElement;
    expect(img).toBeInTheDocument();
    expect(img.src).toContain('/ok.png');
  });

  it('muestra el fallback cuando ocurre un error de carga', async () => {
    const { container } = render(<ImageWithFallback src="/broken.png" alt="img" />);
    const img = screen.getByAltText('img') as HTMLImageElement;

    await act(async () => {
      img.dispatchEvent(new Event('error'));
    });

    // Busca el contenedor de fallback que incluye un img con alt Error loading image
    const fallbackImg = container.querySelector('img[alt="Error loading image"]') as HTMLImageElement | null;
    expect(fallbackImg).not.toBeNull();
    expect(fallbackImg!.getAttribute('data-original-url')).toBe('/broken.png');
  });
});
