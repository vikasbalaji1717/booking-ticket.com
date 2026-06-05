// Ticket Actions Page Helper

document.addEventListener('DOMContentLoaded', () => {
  const printBtn = document.getElementById('print-ticket-btn');
  const pdfBtn = document.getElementById('download-pdf-btn');
  
  if (printBtn) {
    printBtn.addEventListener('click', (e) => {
      e.preventDefault();
      // Simple print utility using browser default print layouts
      window.print();
    });
  }
  
  if (pdfBtn) {
    pdfBtn.addEventListener('click', () => {
      // Backend handles file response streams
      showToast("Preparing your PDF ticket download...", "success");
    });
  }
});
