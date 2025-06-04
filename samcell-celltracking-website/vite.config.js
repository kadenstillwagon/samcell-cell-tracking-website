import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const flask_server = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/get_projects_data': flask_server,
      '/get_cover_image': flask_server,
      '/get_specific_image': flask_server,
      '/get_single_segmentation_mask': flask_server,
      '/get_segmented_cell_image': flask_server,
      '/get_whole_image_with_highlighted_segmentation': flask_server,
      '/upload_image': flask_server,
      '/upload_many_images': flask_server,
      '/add_new_project': flask_server,
      '/get_metrics_with_specific_condition_to_plot': flask_server,
      '/get_metrics_with_specific_condition_to_plot_all_cell_masks': flask_server,
      '/get_metrics_with_specific_condition_to_plot_all_cell_masks_single_image': flask_server,
      '/get_specific_metrics_to_plot': flask_server,
      '/get_specific_metrics_to_plot_all_cell_masks': flask_server,
      '/get_specific_metrics_to_plot_single_image': flask_server,
      '/get_project_data_to_export': flask_server,
      '/get_pca_metrics_all_cell_masks': flask_server,
      '/get_pca_metrics_average_cell_masks': flask_server,
      '/get_pca_metrics_all_cell_masks_single_image': flask_server
    }
  }
})