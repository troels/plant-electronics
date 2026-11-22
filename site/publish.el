;;; publish.el --- export org/ to HTML in public/  -*- lexical-binding: t; -*-

;; Run from anywhere with:  emacs --batch --load site/publish.el
;; Output goes to public/ at the repository root.

(require 'ox-publish)

(let* ((site-dir (file-name-directory (or load-file-name buffer-file-name)))
       (root (file-name-directory (directory-file-name site-dir)))
       (css (with-temp-buffer
              (insert-file-contents (expand-file-name "style.css" site-dir))
              (buffer-string)))
       (nav (concat
             "<nav>"
             "<a class=\"home\" href=\"index.html\">Plant metabolite rig</a>"
             "<a href=\"targets.html\">Targets</a>"
             "<a href=\"rig.html\">Rig</a>"
             "<a href=\"assays.html\">Assays</a>"
             "<a href=\"experiments.html\">Experiments</a>"
             "<a href=\"roadmap.html\">Roadmap</a>"
             "<a href=\"shopping.html\">Shopping</a>"
             "<a href=\"literature.html\">Literature</a>"
             "</nav>")))
  (setq make-backup-files nil
        auto-save-default nil
        org-export-with-broken-links nil
        org-html-doctype "html5"
        org-html-html5-fancy t
        org-html-head-include-default-style nil
        org-html-head-include-scripts nil
        org-html-validation-link nil
        org-publish-use-timestamps-flag nil
        org-publish-timestamp-directory (expand-file-name ".org-timestamps/" root)
        org-publish-project-alist
        `(("site"
           :base-directory ,(expand-file-name "org" root)
           :base-extension "org"
           :publishing-directory ,(expand-file-name "public" root)
           :publishing-function org-html-publish-to-html
           :recursive nil
           :section-numbers nil
           :with-toc 2
           :with-author nil
           :with-creator nil
           :with-properties ("QTY" "EST" "PRICE")
           :html-head ,(concat "<style>\n" css "</style>")
           :html-preamble ,nav
           :html-postamble nil)))
  (org-publish-all t))

;;; publish.el ends here
