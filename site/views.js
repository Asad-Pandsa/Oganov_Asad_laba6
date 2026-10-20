"use strict";

const artistId = document.body.dataset.artistId;
const counter = document.getElementById("view-count");

if (!artistId) {
  throw new Error("Artist page is missing its data-artist-id.");
}

if (!counter) {
  throw new Error("Artist page is missing the view counter.");
}

const storageKey = `artist-views-${artistId}`;
const storedCount = localStorage.getItem(storageKey);
const currentCount = storedCount === null ? 0 : Number(storedCount);

if (!Number.isSafeInteger(currentCount) || currentCount < 0) {
  throw new Error(`Invalid view count stored for ${artistId}.`);
}

const nextCount = currentCount + 1;

if (!Number.isSafeInteger(nextCount)) {
  throw new Error(`View count exceeded the safe integer limit for ${artistId}.`);
}

localStorage.setItem(storageKey, String(nextCount));
counter.textContent = String(nextCount);
