import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),

    // [2026-05-12] DescriptionCallout
    // frontmatter의 description 필드를 NOTE callout으로 렌더링
    // 사용법: md 파일에 description: "설명 텍스트" 추가
    // description이 없으면 렌더링 안 됨
    Component.DescriptionCallout(),

    // [2026-05-12] TableOfContents (본문 상단)
    // 수동 TOC 리스트(마크다운) 대신 Quartz 내장 컴포넌트로 전환
    // md 파일에서 ## 헤딩만 작성하면 자동으로 TOC 생성됨
    // 데스크탑/모바일 모두 본문 상단에 표시
    // 오른쪽 사이드바 TOC(DesktopOnly)와 중복이지만 본문 흐름 파악용으로 유지
    Component.TableOfContents(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({
      folderClickBehavior: "collapse",
      folderDefaultState: "collapsed",
      useSavedState: false,
    }),
  ],
  right: [
    Component.Graph(),
    // [2026-05-12] 오른쪽 사이드바 TOC - 데스크탑 전용
    Component.DesktopOnly(Component.TableOfContents()),
    // [2026-05-12] Backlinks - 다른 문서에서 이 페이지를 [[링크]]로 참조할 때 표시
    // backlink가 0개면 컴포넌트 자체가 렌더링되지 않음
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      folderClickBehavior: "collapse",
      folderDefaultState: "collapsed",
      useSavedState: false,
    }),
  ],
  right: [],
}
