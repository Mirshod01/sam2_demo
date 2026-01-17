/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {Download} from '@carbon/icons-react';
import {useState} from 'react';
import OptionButton from './OptionButton';
import useVideo from '@/common/components/video/editor/useVideo';

export default function ExportYOLOOption() {
  const [isExporting, setIsExporting] = useState(false);
  const video = useVideo();
  const sessionId = video?.sessionId;

  async function handleExport() {
    if (!sessionId) {
      alert('No active session found');
      return;
    }

    setIsExporting(true);

    try {
      const response = await fetch('/export_session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          extract_frames: false,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Export failed');
      }

      // Download the ZIP file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${sessionId}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (error) {
      console.error('Export error:', error);
      alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <OptionButton
      title="Export YOLO Format"
      Icon={Download}
      loadingProps={{
        loading: isExporting,
        label: 'Exporting...',
      }}
      onClick={handleExport}
    />
  );
}
