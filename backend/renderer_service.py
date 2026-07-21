import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from backend.config import IMAGES_DIR

class MathRenderer:
    @staticmethod
    def render_latex(latex_str: str, filename: str) -> Path:
        """
        LaTeX 수식 코드를 투명 배경 300DPI 고해상도 PNG로 렌더링
        """
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(4, 1.5), dpi=300)
        ax.axis('off')
        
        # 수식 렌더링 (LaTeX math mode)
        ax.text(0.5, 0.5, f"${latex_str}$", size=18, ha='center', va='center')
        
        plt.savefig(
            output_path,
            format='png',
            transparent=True,
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )
        plt.close(fig)
        return output_path

    @staticmethod
    def render_geometry_sample(title: str, filename: str) -> Path:
        """
        기하 예시 도형(삼각형/피타고라스 등) 렌더링
        """
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3, 3), dpi=300)
        
        # 직각삼각형 예시 그려주기
        ax.plot([0, 4, 0, 0], [0, 0, 3, 0], color='#2B6CB0', linewidth=2)
        ax.text(2, -0.3, 'a', fontsize=12, ha='center')
        ax.text(-0.3, 1.5, 'b', fontsize=12, va='center')
        ax.text(2.1, 1.6, 'c', fontsize=12)
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 4)
        ax.axis('off')

        plt.savefig(
            output_path,
            format='png',
            transparent=True,
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )
        plt.close(fig)
        return output_path

renderer = MathRenderer()
