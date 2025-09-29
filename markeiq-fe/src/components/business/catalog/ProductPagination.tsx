"use client";

import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { ProductSearchResult } from "@/types/product";

interface ProductPaginationProps {
  searchResult: ProductSearchResult | null;
  currentPage: number;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export function ProductPagination({
  searchResult,
  currentPage,
  onPageChange,
  loading = false
}: ProductPaginationProps) {
  if (!searchResult || searchResult.total_pages <= 1) {
    return null;
  }

  const totalPages = searchResult.total_pages;
  const maxVisiblePages = 5;
  
  // Calculate the range of pages to show
  const getVisiblePages = () => {
    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const half = Math.floor(maxVisiblePages / 2);
    let start = Math.max(1, currentPage - half);
    const end = Math.min(totalPages, start + maxVisiblePages - 1);

    // Adjust start if we're near the end
    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  };

  const visiblePages = getVisiblePages();
  const showStartEllipsis = visiblePages[0] > 1;
  const showEndEllipsis = visiblePages[visiblePages.length - 1] < totalPages;

  const handlePageClick = (page: number) => {
    if (page !== currentPage && !loading) {
      onPageChange(page);
      // Scroll to top when page changes
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 mt-8">
      {/* Results summary */}
      <div className="text-sm text-muted-foreground text-center">
        Page no. {currentPage} and {" "}
        {Math.min(searchResult.limit, searchResult.total - (currentPage - 1) * searchResult.limit)}{' '}
        of {searchResult.total.toLocaleString()} results
      </div>

      {/* Pagination */}
      <Pagination>
        <PaginationContent>
          {/* Previous button */}
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (currentPage > 1 && !loading) {
                  handlePageClick(currentPage - 1);
                }
              }}
            />
          </PaginationItem>

          {/* First page */}
          {showStartEllipsis && (
            <>
              <PaginationItem>
                <PaginationLink
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handlePageClick(1);
                  }}
                  isActive={currentPage === 1}
                  className="hover:bg-primary/10"
                >
                  1
                </PaginationLink>
              </PaginationItem>
              {visiblePages[0] > 2 && (
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
              )}
            </>
          )}

          {/* Visible page numbers */}
          {visiblePages.map((page) => (
            <PaginationItem key={page}>
              <PaginationLink
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handlePageClick(page);
                }}
                isActive={currentPage === page}
              >
                {page}
              </PaginationLink>
            </PaginationItem>
          ))}

          {/* Last page */}
          {showEndEllipsis && (
            <>
              {visiblePages[visiblePages.length - 1] < totalPages - 1 && (
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
              )}
              <PaginationItem>
                <PaginationLink
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handlePageClick(totalPages);
                  }}
                  isActive={currentPage === totalPages}
                  className="hover:bg-primary/10"
                >
                  {totalPages}
                </PaginationLink>
              </PaginationItem>
            </>
          )}

          {/* Next button */}
          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (currentPage < totalPages && !loading) {
                  handlePageClick(currentPage + 1);
                }
              }}
              className={`${
                currentPage >= totalPages || loading
                  ? 'pointer-events-none opacity-50'
                  : 'hover:bg-primary/10'
              }`}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>

    </div>
  );
}
