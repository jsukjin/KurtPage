// [2026-05-12] DescriptionCallout 컴포넌트
// frontmatter의 description 필드를 NOTE callout 형태로 본문 상단에 표시
// quartz.layout.ts의 beforeBody에 추가해서 사용
// 사용법: md 파일 frontmatter에 description: "내용" 추가

import { QuartzComponentConstructor, QuartzComponentProps } from "./types"

export default (() => {
  function DescriptionCallout({ fileData }: QuartzComponentProps) {
    const description = fileData.frontmatter?.description as string | undefined
    if (!description) return null

    return (
      <div class="callout note" data-callout="note">
        <div class="callout-title">
          <div class="callout-icon"></div>
          <div class="callout-title-inner">NOTE</div>
        </div>
        <div class="callout-content">
          <p>{description}</p>
        </div>
      </div>
    )
  }

  return DescriptionCallout
}) satisfies QuartzComponentConstructor
